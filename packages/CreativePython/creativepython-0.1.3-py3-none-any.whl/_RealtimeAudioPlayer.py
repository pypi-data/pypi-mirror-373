#######################################################################################
# _RealtimeAudioPlayer.py       Version 1.0     22-Aug-2025
# Trevor Ritchie, Taj Ballinger, and Bill Manaris
#
#######################################################################################
#
# [LICENSING GOES HERE]
#
#######################################################################################
# TODO:
#
#######################################################################################

import sounddevice as sd  # for audio playback
import soundfile as sf    # for audio file reading
import numpy as np        # for array operations
import os                 # for file path operations
import math               # for logarithmic calculations in pitch/frequency conversions


#### Helper Functions #################################################################

def freqToNote(frequency):
   """Converts frequency to the closest MIDI note number with pitch bend value
      for finer control.  A4 corresponds to the note number 69 (concert pitch
      is set to 440Hz by default).  The default pitch bend range is 4 half tones,
      and ranges from -8191 to +8192 (0 means no pitch bend).
   """

   concertPitch = 440.0   # 440Hz
   bendRange = 4          # 4 semitones (2 below, 2 above)

   x = math.log(frequency / concertPitch, 2) * 12 + 69
   pitch = round(x)
   pitchBend = round((x - pitch) * 8192 / bendRange * 2)

   return int(pitch), int(pitchBend)


def noteToFreq(pitch):
   """Converts a MIDI pitch to the corresponding frequency.  A4 corresponds to the note number 69 (concert pitch
      is set to 440Hz by default).
   """

   concertPitch = 440.0   # 440Hz

   frequency = concertPitch * 2 ** ( (pitch - 69) / 12.0 )

   return frequency


##### Real-Time Audio Player Class ########################################################

class _RealtimeAudioPlayer:
   """
   This class is used by AudioSample to provide low-level, realtime audio playback
   functionality. AudioSample acts as a higher-level interface for musical and polyphonic
   control, but delegates all actual audio streaming, pitch/frequency shifting, volume, and
   panning operations to _RealtimeAudioPlayer. By encapsulating the playback logic here,
   AudioSample can manage multiple voices, envelopes, and advanced features without
   duplicating audio I/O code.
   """

   def __init__(self, filepath, loop=False, actualPitch=69, chunkSize=1024):
      """
      Initialize a realtime audio player for the specified audio file.

      filepath:    path to the audio file to load and play
      loop:        whether to loop the audio playback (default: False)
      actualPitch: MIDI pitch (0-127) representing the base frequency of the audio (default: 69 for A4)
      chunkSize:   size of audio chunks for realtime processing (default: 1024 frames)
      """

      # validate that the audio file exists
      if not os.path.isfile(filepath):
         raise ValueError(f"File not found: {filepath}")

      self.filepath = filepath   # store the file path for reference

      # load the audio file using soundfile library
      try:
         self.audioData, self.sampleRate = sf.read(filepath, dtype='float32')

      except Exception as e:
         print(f"Error loading audio file with soundfile: {e}")
         raise

      # analyze audio file structure and validate format compatibility
      if self.audioData.ndim == 1:
         self.numChannels = 1   # single channel (mono) audio
         self.numFrames = len(self.audioData)

      elif self.audioData.ndim == 2:
         self.numChannels = self.audioData.shape[1]   # multi-channel audio (stereo = 2)
         self.numFrames = self.audioData.shape[0]

         if self.numChannels > 2:   # restrict to mono/stereo for current implementation
            raise ValueError(f"Unsupported number of channels: {self.numChannels}. Max 2 channels supported.")

      else:
         raise ValueError(f"Unexpected audio data dimensions: {self.audioData.ndim}")

      # check if the audio file contains any actual audio data
      if self.numFrames == 0:
         print(f"Warning: Audio file '{os.path.basename(self.filepath)}' contains zero audio frames and is unplayable.")

      # initialize playback state attributes
      self.isPlaying = False                    # track whether audio is currently playing
      self.playbackPosition = 0.0               # current playback position in frames
      self.looping = loop                       # whether to loop the audio
      self.rateFactor = 1.0                     # playback speed multiplier (1.0 = normal speed)
      self.volumeFactor = 1.0                   # volume multiplier (1.0 = normal volume)

      # initialize panning attributes for stereo positioning
      self.panTargetFactor = 0.0                # target pan position (-1.0 = left, 0.0 = center, 1.0 = right)
      self.currentPanFactor = 0.0               # current pan position
      self.panInitialFactor = 0.0               # pan position when smoothing began
      self.panSmoothingDurationMs = 100         # duration of pan smoothing in milliseconds
      self.panSmoothingTotalFrames = max(1, int(self.sampleRate * (self.panSmoothingDurationMs / 1000.0)))   # convert to frames
      self.panSmoothingFramesProcessed = self.panSmoothingTotalFrames   # start as if complete

      # initialize pitch and frequency attributes
      validPitchProvided = False
      if isinstance(actualPitch, (int, float)):
         tempPitch = float(actualPitch)

         if 0 <= tempPitch <= 127:   # validate MIDI pitch range
            self.basePitch = tempPitch
            self.baseFrequency = noteToFreq(self.basePitch)   # convert MIDI pitch to frequency
            validPitchProvided = True

      if not validPitchProvided:
         # handle invalid pitch values by defaulting to A4 (440Hz)
         print(f"Warning: Invalid or out-of-range actualPitch ({actualPitch}) provided for '{os.path.basename(self.filepath)}'. Expected MIDI pitch (int/float) 0-127. Defaulting to A4 (69 / 440Hz).")
         self.basePitch = 69.0   # default MIDI A4
         self.baseFrequency = noteToFreq(self.basePitch)   # default 440 Hz

      # initialize fade-in attributes for smooth audio start (avoid pops/cracks)
      self.fadeInDurationMs = 20                # fade-in duration in milliseconds
      self.fadeInTotalFrames = max(1, int(self.sampleRate * (self.fadeInDurationMs / 1000.0)))   # convert to frames
      self.fadeInFramesProcessed = 0            # frames processed during current fade-in
      self.isApplyingFadeIn = False             # whether fade-in is currently active

      # initialize fade-out attributes for smooth audio stop (avoid pops/cracks)
      self.fadeOutDurationMs = 20               # fade-out duration in milliseconds
      self.fadeOutTotalFrames = max(1, int(self.sampleRate * (self.fadeOutDurationMs / 1000.0)))   # convert to frames
      self.fadeOutFramesProcessed = 0           # frames processed during current fade-out
      self.isApplyingFadeOut = False            # whether fade-out is currently active
      self.isFadingOutToStop = False            # whether fade-out is leading to a stop

      # initialize seek fade attributes for smooth position changes
      self.isFadingOutToSeek = False            # whether fade-out is leading to a seek operation
      self.seekTargetFrameAfterFade = 0.0       # target frame position after seek fade completes

      # initialize sounddevice stream attributes
      self.sdStream = None                      # sounddevice audio stream for realtime playback
      self.chunkSize = chunkSize                # size of audio chunks for processing

      # initialize internal state attributes
      self.playbackEndedNaturally = False       # whether playback ended naturally (not stopped)
      self.playDurationSourceFrames = -1.0      # specific play duration in source frames (-1 = play to end)
      self.targetEndSourceFrame = -1.0          # target end frame for specific play duration (-1 = play to end)

      # initialize loop control attributes
      self.loopRegionStartFrame = 0.0           # start frame of loop region
      self.loopRegionEndFrame = -1.0            # end frame of loop region (-1 means to end of file)
      self.loopCountTarget = -1                 # target loop count (-1 = infinite, 0 = no loop, 1+ = specific count)
      self.loopsPerformed = 0                   # number of loops completed so far

      if self.looping and self.loopCountTarget == -1:   # default constructor loop is infinite
         pass   # loopCountTarget remains -1

      elif not self.looping:   # not looping
         self.loopCountTarget = 0   # play once then stop

      # print(f"For '{os.path.basename(self.filepath)}', BasePitch={self.basePitch:.2f}, BaseFreq={self.baseFrequency:.2f}Hz.")


   def _findNextZeroCrossing(self, startFrameFloat, searchWindowFrames=256):
      """
      Finds the nearest zero-crossing at or after startFrameFloat.
      Looks within a small window to avoid long searches.
      Returns the frame index (float) of the sample that is at or just after the zero-crossing.
      If no crossing is found within the window, returns the original startFrame, clamped to audio bounds.
      """

      startFrame = int(math.floor(startFrameFloat))
      startFrame = max(0, min(startFrame, self.numFrames - 1))

      # limit search window to prevent going beyond audio data boundaries
      endSearchFrame = min(self.numFrames - 1, startFrame + searchWindowFrames)

      if startFrame >= self.numFrames -1:   # if already at or past the second to last frame
         return float(min(startFrame, self.numFrames -1))

      # iterate through the audio frames in the search window to find a zero-crossing
      for frameIdx in range(startFrame, endSearchFrame):
         currentSample = 0.0
         nextSample = 0.0

         if self.numChannels == 1:   # mono audio
            currentSample = self.audioData[frameIdx]
            if frameIdx + 1 < self.numFrames:
               nextSample = self.audioData[frameIdx + 1]
            else:
               return float(frameIdx) # reached end

         elif self.numChannels >= 2:   # stereo (or more)
            currentSample = self.audioData[frameIdx, 0]
            if frameIdx + 1 < self.numFrames:
               nextSample = self.audioData[frameIdx + 1, 0]
            else:
               return float(frameIdx) # reached end

         # is current sample exactly zero? (a zero-crossing point)
         if currentSample == 0.0:
            return float(frameIdx)   # return frame index

         # is there a sign change between currentSample and nextSample?
         # ...which indicates a zero-crossing between these two samples
         if (currentSample > 0 and nextSample <= 0) or \
            (currentSample < 0 and nextSample >= 0):
            # return the frame index just after the crossing (i+1)
            return float(frameIdx + 1)   # closest we can get to zero-crossing

      return float(startFrame)   # no crossing found in window


   def setRateFactor(self, factor):
      # check if the provided factor is a number (int or float)
      if isinstance(factor, (int, float)):

         # if factor is zero or negative, set to a very small positive value to effectively pause playback
         if factor <= 0:
            self.rateFactor = 0.00001   # avoid zero or negative, effectively silent/pause

         else:
            # otherwise, set the rate factor to the given value (as float)
            self.rateFactor = float(factor)
         # print(f"Set to {self.rateFactor:.4f}")

      else:
         # if input is not a number, default to 1x speed
         self.rateFactor = 1.0


   def getRateFactor(self):
      return self.rateFactor   # return rate factor


   def setVolumeFactor(self, factor):
      if isinstance(factor, (int, float)):
         # valid factor, so set volume
         self.volumeFactor = max(0.0, min(1.0, float(factor)))
         # print(f"Set to {self.volumeFactor:.3f}")

      else:
         # factor is invalid type, so default to full volume
         self.volumeFactor = 1.0


   def getVolumeFactor(self):
      return self.volumeFactor   # return volume factor


   def setPanFactor(self, panFactor):
      # clamp panFactor to a float in [-1.0, 1.0]; if invalid, default to center (0.0)
      if not isinstance(panFactor, (int, float)):
         clampedPanFactor = 0.0   # not a number, so use center

      else:
         clampedPanFactor = max(-1.0, min(1.0, float(panFactor)))   # clamp to valid range

      # if the new pan target is different enough from the current target, start smoothing ramp
      if abs(self.panTargetFactor - clampedPanFactor) > 0.001:   # significant change
         self.panTargetFactor = clampedPanFactor   # set new pan target
         self.panInitialFactor = self.currentPanFactor   # remember current pan as ramp start
         self.panSmoothingFramesProcessed = 0   # reset smoothing progress


   def getPanFactor(self):
      return self.panTargetFactor   # return pan factor


   def setFrequency(self, targetFrequencyHz):
      if isinstance(targetFrequencyHz, (int, float)) and self.baseFrequency > 0:

         if targetFrequencyHz > 0:   # frequency is valid
            newRateFactor = targetFrequencyHz / self.baseFrequency
            self.setRateFactor(newRateFactor)

         else:   # target frequency too small
            self.setRateFactor(0.00001)   # avoid zero or negative, effectively silent/pause


   def getFrequency(self):
      # calculate current frequency based on base and rate
      currentFreq = self.baseFrequency * self.rateFactor
      return currentFreq   # return current frequency


   def setPitch(self, midiPitch):
      # set the playback pitch by converting midiPitch (0-127) to frequency and updating rate factor
      if (isinstance(midiPitch, (int, float)) and 0 <= midiPitch <= 127):
         targetFrequencyHz = noteToFreq(float(midiPitch))   # convert midi pitch to frequency
         self.setFrequency(targetFrequencyHz)               # set playback frequency accordingly


   def getPitch(self):
      currentFreq = self.getFrequency()        # get freq
      currentPitch = freqToNote(currentFreq)   # convert to pitch
      return currentPitch   # return current pitch


   def getBasePitch(self):
      return self.basePitch   # original pitch of the sample


   def getBaseFrequency(self):
      return self.baseFrequency   # original frequency of the sample


   def getFrameRate(self):
      return self.sampleRate   # sample rate of the audio


   def getCurrentTime(self):
      # calculate current time based on position and sample rate
      currentTime = self.playbackPosition / self.sampleRate
      return currentTime   # return current time


   def setCurrentTime(self, timeSeconds):
      # check that timeSeconds is a valid non-negative number. if not, default to 0.0
      if not isinstance(timeSeconds, (int, float)) or timeSeconds < 0:
         timeSeconds = 0.0

      # convert the requested time in seconds to a floating-point frame index
      originalTargetFrameFloat = timeSeconds * self.sampleRate

      # basic ZC adjustment for now, will be enhanced with fade-seek-fade
      actualTargetFrame = self.findNextZeroCrossing(originalTargetFrameFloat)

      # if playing and conditions met for smooth seek
      if actualTargetFrame >= self.numFrames and not self.looping:
         # set playback position to the requested frame, or to the end if beyond available frames
         self.playbackPosition = float(self.numFrames -1)
         self.playbackEndedNaturally = True

      else:
         self.playbackPosition = actualTargetFrame   # set playback position to the next zero crossing
         self.playbackEndedNaturally = False   # reset natural end flag if jumping


   ### Playback Control Methods ########################################################################

   def audioCallback(self, outdata, frames, time, status):
      """
      This is the core audio processing callback.
      It's called by sounddevice when it needs more audio data.

      Parameters:
      outdata (numpy.ndarray): A NumPy array that this function needs to fill with audio data.
                               This is what will be sent to the sound card.
                               Its shape is (frames, numOutputChannels).
      frames (int): The number of audio frames (samples per channel) that sounddevice expects
                    this function to produce.
      time (sounddevice. beggeback object): Contains various timestamps related to the audio stream.
                                      `time.currentTime` is the time at the sound card when the first
                                      sample of `outdata` will be played.
                                      `time.inputBufferAdcTime` is the capture time of the first input sample (if input stream).
                                      `time.outputBufferDacTime` is the time the first output sample will be played.
      status (sounddevice.CallbackFlags): Flags indicating if any stream errors (e.g., input overflow,
                                         output underflow) have occurred. It's good practice to check
                                         this, though for simplicity in many examples it might be ignored.
      """

      # if status:
      #    print(f"Status flags: {status}") # keep this commented unless debugging status

      # failsafe for zero-frame audio, though play() should prevent this stream from starting.
      if self.numFrames == 0:
         outdata.fill(0) # fill the output buffer with silence.

         if self.isPlaying: # this should ideally not be true if play() did its job
            self.isPlaying = False # ensure playback state is consistent.

         raise sd.CallbackStop # stop the callback immediately, as there's no audio to play.

      # If not playing or rate is effectively zero, output silence.
      # This handles cases where playback is paused, explicitly stopped, or the playback rate
      # is so low that it's practically silent. This is a quick way to silence output
      # without needing to go through the whole processing loop.
      if not self.isPlaying or self.rateFactor <= 0.000001:
         outdata.fill(0) # fill the output buffer with silence.

         if self.isApplyingFadeOut and self.isFadingOutToStop and self.rateFactor <= 0.000001:
            # If a fade-out to stop was in progress and the rate also became zero (e.g. set externally),
            # ensure the player state is fully stopped.
            self.isPlaying = False
            self.isApplyingFadeOut = False
            self.isFadingOutToStop = False
            # no need to raise CallbackStop here, as returning normally from a callback while
            # the stream is active and isPlaying is false will lead to it being stopped by play/stop logic.

         return # exit the callback early, providing silence.

      numOutputChannels = outdata.shape[1]   # get number of output channels (1=mono, 2=stereo)

      # initialize chunkBuffer matching the output stream's channel count and frame count for this callback.
      # This buffer will be filled with processed audio samples one by one before being copied to `outdata`.
      # Using an intermediate buffer like this is common for clarity and for complex processing steps.
      chunkBuffer = np.zeros((frames, numOutputChannels), dtype=np.float32)

      for i in range(frames): # per-sample processing loop

         if not self.isPlaying: # check if stop was called or playback ended within the loop

            # If isPlaying became false (e.g., due to a fade-out completing and setting isPlaying to False,
            # or an external stop() call), we should fill the rest of this chunk with silence
            # and then break out of this sample-processing loop.
            chunkBuffer[i:] = 0.0 # fill remaining part of the buffer with silence
            break # exit per-sample loop
            # TODO: rewrite to avoid early break

         #### Determine current sample value with interpolation (and hard loop if enabled)
         # To play audio at different speeds (self.rateFactor != 1.0) or for smooth playback,
         # we often need a sample value that lies *between* two actual data points in our audioData.
         # Linear interpolation is a common way to estimate this value.
         readPosFloat = self.playbackPosition          # float indicating the conceptual read position
         readPosInt1 = int(math.floor(readPosFloat))   # the integer part, an index to an actual sample
         readPosInt2 = readPosInt1 + 1                 # next actual sample index
         fraction = readPosFloat - readPosInt1         # the fractional part, how far between readPosInt1 and readPosInt2 we are.

         # Clamp read positions to be safe for array access, *after* potential looping adjustment
         # This ensures that we don't try to read outside the bounds of our audioData array.
         readPosInt1 = max(0, min(readPosInt1, self.numFrames - 1))   # ensure read position 1 is valid
         readPosInt2 = max(0, min(readPosInt2, self.numFrames - 1))   # ensure read position 2 is also valid

         # get interpolated sample from self.audioData
         currentSampleArray = np.zeros(self.numChannels, dtype=np.float32)

         if self.numChannels == 1:   # mono audio source
            sampleValue1 = self.audioData[readPosInt1]   # first sample value

            # if there is only one frame, use sampleValue1 for both; otherwise, get the next sample
            if self.numFrames > 1:
               sampleValue2 = self.audioData[readPosInt2]   # second sample value

            else:
               sampleValue2 = sampleValue1   # only one frame, so repeat

            #### Perform linear interpolation between the two sample values.
            # NOTE: This is necessary because playback speed (rateFactor) may not be exactly 1.0,
            # so the read position can fall between two discrete audio samples.
            # Linear interpolation estimates the sample value at this fractional position,
            # resulting in smoother pitch shifting and time stretching, and avoids artifacts
            # that would occur if we simply rounded to the nearest sample.
            interpolatedValue = sampleValue1 + (sampleValue2 - sampleValue1) * fraction
            currentSampleArray[0] = interpolatedValue   # store result in output array

         else: # stereo source
            # for stereo, we interpolate each channel (Left and Right) independently.
            sampleValue1_L = self.audioData[readPosInt1, 0]   # Left channel, first sample
            sampleValue2_L = self.audioData[readPosInt2 if self.numFrames > 1 else readPosInt1, 0]   # left channel, second sample
            currentSampleArray[0] = sampleValue1_L + (sampleValue2_L - sampleValue1_L) * fraction    # interpolated left channel

            sampleValue1_R = self.audioData[readPosInt1, 1] # right channel, first sample
            sampleValue2_R = self.audioData[readPosInt2 if self.numFrames > 1 else readPosInt1, 1]   # right channel, second sample
            currentSampleArray[1] = sampleValue1_R + (sampleValue2_R - sampleValue1_R) * fraction    # interpolated right channel

         #### Apply Volume (Volume is applied first before fades)
         # the overall volume of the sample is scaled by self.volumeFactor
         processedSample = currentSampleArray * self.volumeFactor

         #### Apply Master Fades (Fade-in and Fade-out) ---
         # Fades are applied by smoothly changing a gain envelope from 0 to 1 (fade-in)
         # or 1 to 0 (fade-out) over a specified number of frames.
         gainEnvelope = 1.0 # start with full gain, adjust if fading.

         if self.isApplyingFadeIn:   # is fade-in currently being applied?

            if self.fadeInFramesProcessed < self.fadeInTotalFrames:   # check if fade-in is still in progress
               # Calculate gain based on how many fade-in frames have been processed.
               # This creates a linear ramp from 0.0 to 1.0.
               gainEnvelope *= (self.fadeInFramesProcessed / self.fadeInTotalFrames)   # ramp from 0 to 1
               self.fadeInFramesProcessed += 1   # increment frame

            else:   # fade-in complete
               self.isApplyingFadeIn = False   # stop applying fade-in for subsequent samples.
               # gainEnvelope is already 1.0, fadeInFramesProcessed is capped by play() or setter

         if self.isApplyingFadeOut:   # is fade-out currently being applied?

            if self.fadeOutFramesProcessed < self.fadeOutTotalFrames:   # is fade-out still in progress?
               currentFadeOutProgress = self.fadeOutFramesProcessed / self.fadeOutTotalFrames

               # Calculate gain based on how many fade-out frames have been processed.
               # This creates a linear ramp from 1.0 down to 0.0.
               gainEnvelope *= (1.0 - currentFadeOutProgress) # ramp from 1 to 0
               self.fadeOutFramesProcessed += 1

            else:   # fade-out complete
               gainEnvelope = 0.0 # ensure silence
               self.isApplyingFadeOut = False # stop applying fade-out.

               if self.isFadingOutToStop:   #  was fade-out triggered by a stop request?
                  # If this fade-out was intended to stop playback (e.g., user called stop()),
                  # set isPlaying to False. This will be caught at the start of the next
                  # sample processing iteration or at the end of this audio block.
                  self.isPlaying = False   # this will be caught at start of next sample or end of block
                  self.isFadingOutToStop = False
                  self.targetEndSourceFrame = -1.0       # reset
                  self.playDurationSourceFrames = -1.0   # reset

         processedSample = processedSample * gainEnvelope   # apply the combined fade gain to the sample

         #### Apply Panning (to the already faded and volume-adjusted sample)
         finalOutputSample = np.zeros(numOutputChannels, dtype=np.float32)

         if numOutputChannels == 2: # stream is stereo
            panValue = self.currentPanFactor # use smoothed value updated at end of block

            #### Standard psychoacoustic panning law (constant power)
            # NOTE: This formula ensures that the total perceived loudness remains relatively constant
            # as the sound is panned from left to right.
            # pan value from -1 (L) to 0 (C) to 1 (R)
            # angle goes from 0 (L) to PI/4 (C) to PI/2 (R)
            panAngleRad = (panValue + 1.0) * math.pi / 4.0 # convert panValue to an angle
            leftGain = math.cos(panAngleRad)  # gain for the left channel
            rightGain = math.sin(panAngleRad) # gain for the right channel

            if self.numChannels == 1: # mono source to stereo output
               # apply panning gains to the single source channel for stereo output
               finalOutputSample[0] = processedSample[0] * leftGain
               finalOutputSample[1] = processedSample[0] * rightGain

            else: # stereo source to stereo output
               # Apply panning gains to each respective channel of the stereo source.
               # NOTE: This is a simple pan of a stereo source. More sophisticated stereo
               # panners might treat the channels differently (e.g., balance control).
               finalOutputSample[0] = processedSample[0] * leftGain
               finalOutputSample[1] = processedSample[1] * rightGain

         else: # stream is mono

            if self.numChannels == 1: # mono source to mono output
               # no panning needed, just pass the sample through.
               finalOutputSample[0] = processedSample[0]

            else: # stereo source to mono output (mix down)
               # Mix the left and right channels of the stereo source to a single mono channel.
               # The 0.5 factor helps prevent clipping when combining channels.
               finalOutputSample[0] = (processedSample[0] + processedSample[1]) * 0.5   # mixdown with gain to avoid clipping

         # now, the output sample is processed
         chunkBuffer[i] = finalOutputSample   # store the processed output sample in the chunk buffer

         #### Advance Playback Position for next sample
         # self.playbackPosition is advanced by self.rateFactor. If rateFactor is 1.0, it moves one sample forward.
         # If rateFactor is 0.5, it effectively plays at half speed (each source sample is held for two output samples, due to interpolation).
         # If rateFactor is 2.0, it plays at double speed (skipping source samples, with interpolation filling the gaps).
         self.playbackPosition += self.rateFactor

         # This is the point at which we should either loop or stop for the current play segment,
         # so determine the effective end frame for the current segment/loop
         effectiveSegmentEndFrame = self.numFrames -1 # default to end of file

         if self.looping and self.loopRegionEndFrame > 0:
            # if looping and a specific loop region end is defined, that's our segment end
            effectiveSegmentEndFrame = self.loopRegionEndFrame

         elif not self.looping and self.targetEndSourceFrame > 0: # play(size) scenario
            # if not looping, but a specific duration was given (play(size)), that defines the segment end
            effectiveSegmentEndFrame = self.targetEndSourceFrame

         # check for end of segment (loop iteration, play(size) duration, or natural EOF)
         if self.playbackPosition >= effectiveSegmentEndFrame:

            # we've reached or passed the end of the current audio segment
            if self.looping:
               self.loopsPerformed += 1

               if self.loopCountTarget != -1 and self.loopsPerformed >= self.loopCountTarget:
                  # If we've reached the target number of loops (and it's not infinite looping),
                  # stop playback.
                  self.isPlaying = False
                  self.loopsPerformed = 0 # reset for next play call
                  # other loop params (loopCountTarget, loopRegionStartFrame, loopRegionEndFrame) are reset by play()

               else: # continue looping (either infinite or more loops to go)
                  # wrap position back to the start of the loop region
                  # This causes playback to jump back to self.loopRegionStartFrame to continue the loop.
                  self.playbackPosition = self.loopRegionStartFrame

            else: # not looping, and reached end of specified segment or natural EOF
               # this handles both play(size) completion and natural end of a non-looping file.
               self.isPlaying = False # stop playback.

               if self.playbackPosition >= self.numFrames -1: # check if it was natural EOF
                  # If we've also reached or passed the actual end of the audio file data,
                  # mark that playback ended naturally.
                  self.playbackEndedNaturally = True

               # reset play(size) parameters if they were active
               self.targetEndSourceFrame = -1.0
               self.playDurationSourceFrames = -1.0
               # loop counters are reset by play() or if explicitly stopped.
               # self.loopsPerformed = 0 # reset here too just in case.

         #### Post-loop/end-of-segment logic, check if isPlaying is still true before interpolation
         # NOTE: This check is crucial. If the logic above (loop completion, segment end) set isPlaying to False,
         # we need to fill the rest of the current audio chunk with silence and exit the sample loop.
         if not self.isPlaying:
            chunkBuffer[i:] = 0.0 # fill remaining part of this chunk with silence
            break # exit per-sample loop
            # TODO: rewrite to avoid break

      #### End of per-sample loop (for i in range(frames))

      #### Update smoothed pan factor (block-level, after all samples in this chunk are processed)
      # NOTE: To avoid abrupt changes in panning, which can sound like clicks or pops,
      # we smoothly transition the self.currentPanFactor towards self.panTargetFactor over
      # a short duration (self.panSmoothingTotalFrames).
      # This calculation is done once per audio block rather than per sample
      # for efficiency, and because per-sample smoothing would be overkill.
      # check if pan smoothing is still in progress for this block
      if self.panSmoothingFramesProcessed < self.panSmoothingTotalFrames:
         self.panSmoothingFramesProcessed += frames   # accumulate frames processed in this callback

         # check if smoothing has now reached or exceeded the total smoothing duration
         if self.panSmoothingFramesProcessed >= self.panSmoothingTotalFrames:
            self.currentPanFactor = self.panTargetFactor   # target reached, snap to it
            self.panSmoothingFramesProcessed = self.panSmoothingTotalFrames   # cap it

         else:
            # smoothing is still in progress, so interpolate current pan factor for the block
            # t is the fraction of the smoothing duration that has passed
            t = self.panSmoothingFramesProcessed / self.panSmoothingTotalFrames
            self.currentPanFactor = self.panInitialFactor + (self.panTargetFactor - self.panInitialFactor) * t

      else:   # smoothing is complete or wasn't active for this block duration
         self.currentPanFactor = self.panTargetFactor   # ensure it's at target if smoothing just finished or was already done

      #### Copy the fully processed chunkBuffer to the output buffer for sounddevice
      # NOTE: Audio samples should typically be within the range -1.0 to 1.0.
      # np.clip ensures that any values outside this range (due to processing, bugs, or loud source material)
      # are clamped to the min/max, preventing potential distortion or errors in the audio output driver.
      outdata[:] = np.clip(chunkBuffer, -1.0, 1.0)

      #### Handle stream stopping conditions
      # NOTE: If isPlaying became False during this callback (e.g., by fade-out completion or natural end)
      # raise CallbackStop to tell PortAudio to stop invoking this callback.
      # This is the primary mechanism for cleanly stopping the audio stream from within the callback
      # when playback is logically complete or has been requested to stop.
      if not self.isPlaying:
         raise sd.CallbackStop

      #### end of audioCallback


   def play(self, startAtBeginning=True, loop=None, playDurationSourceFrames=-1.0,
            loopRegionStartFrame=0.0, loopRegionEndFrame=-1.0, loopCountTarget=None,
            initialLoopsPerformed=0):

      # does audio file contain zero frames?
      if self.numFrames == 0:
         # if so, do not attempt to play
         print(f"Cannot play '{os.path.basename(self.filepath)}' as it contains zero audio frames.")
         self.isPlaying = False   # ensure state consistency
         return   # do not proceed to start a stream
         # TODO: rewrite to avoid early return

      # is a fade-out to stop currently in progress?
      if self.isFadingOutToStop:
         # if so, reset fade-out state before playing
         self.isApplyingFadeOut = False
         self.isFadingOutToStop = False
         self.fadeOutFramesProcessed = 0

      # determine definitive looping state and count from parameters
      if loop is not None:
         self.looping = bool(loop)

      elif loopCountTarget is not None: # loop is None, derive from loopCountTarget
         self.looping = True if loopCountTarget != 0 else False

      # Now, if both loop and loopCountTarget are None, self.looping is unchanged (relevant if stream is already playing)
      # or takes its initial value from __init__ if stream is being started for the first time.

      # determine how many times to loop (or not) based on input and current looping state
      if loopCountTarget is not None:
         self.loopCountTarget = loopCountTarget   # use the provided loop count

      elif self.looping:   # no explicit loop count, but looping is enabled
         self.loopCountTarget = -1   # default to infinite looping

      else:   # not looping and no loop count specified
         self.loopCountTarget = 0   # play once by default

      # ensure consistency: if loopCountTarget implies a certain looping state, it can refine self.looping
      if self.loopCountTarget == 0: # explicitly play once for this segment
         self.looping = False

      elif self.loopCountTarget == -1 or self.loopCountTarget > 0: # infinite or positive count implies looping
         self.looping = True

      # store parameters
      self.playDurationSourceFrames = playDurationSourceFrames   # used if not self.looping
      self.loopRegionStartFrame = max(0.0, float(loopRegionStartFrame))
      self.loopRegionEndFrame = float(loopRegionEndFrame) if loopRegionEndFrame is not None else -1.0

      # adjust the loop region end frame so it does not exceed the last valid frame in the audio file
      if self.loopRegionEndFrame > 0:
         self.loopRegionEndFrame = min(self.loopRegionEndFrame, self.numFrames - 1 if self.numFrames > 0 else 0.0)

      # ensure the loop region is valid: if the start frame is after or equal to the end frame, reset to default (full file)
      if self.numFrames > 0 and self.loopRegionEndFrame > 0 and self.loopRegionStartFrame >= self.loopRegionEndFrame:
         self.loopRegionStartFrame = 0.0
         self.loopRegionEndFrame = -1.0   # default to looping the entire file

      # determine the stopping point for playback based on looping and duration settings
      if self.looping:
         # when looping, ignore playDurationSourceFrames and play until loop count is reached or forever
         self.targetEndSourceFrame = -1.0

      elif self.playDurationSourceFrames >= 0:
         # when not looping but a specific play duration is requested, calculate the end frame for playback
         currentStartForCalc = self.playbackPosition if not startAtBeginning else self.loopRegionStartFrame
         self.targetEndSourceFrame = currentStartForCalc + self.playDurationSourceFrames
         # self.loopCountTarget is already 0 if not looping

      else:
         # when not looping and no duration is specified, play until the natural end of the file
         self.targetEndSourceFrame = -1.0
         # self.loopCountTarget is already 0

      # handle playback position and loops performed count based on startAtBeginning and initialLoopsPerformed
      if startAtBeginning:
         self.playbackPosition = self.loopRegionStartFrame # start at the beginning of the loop region (or 0 if not specified)
         self.loopsPerformed = initialLoopsPerformed # typically 0 for a fresh start from beginning

      else: # resuming (startAtBeginning=False)
         # playbackPosition is where it was left off by pause or setCurrentTime
         self.loopsPerformed = initialLoopsPerformed   # restore from argument

      self.playbackEndedNaturally = False   # reset this flag as we are starting/resuming a play action

      # if already playing, these settings will take effect, but stream isn't restarted

      # if not playing, start the stream.
      if not self.isPlaying:

         if self.playbackPosition >= self.numFrames and not self.looping:
            self.playbackPosition = 0.0 # or self._findNextZeroCrossing(0.0)

         self.playbackEndedNaturally = False   # playback did not reach the end

         try:
            # always start with a fade-in when initiating play from a stopped state or from a fade-out-to-stop state
            self.isApplyingFadeIn = True
            self.fadeInFramesProcessed = 0

            if self.sdStream and not self.sdStream.closed:
               # NOTE: If stream exists but was stopped (e.g. by isPlaying = False in callback)
               # It needs to be closed and reopened, or sounddevice's start() might not work as expected
               # or might resume from an odd state. Safest is to ensure clean start.
               self.sdStream.close() # ensure previous instance is closed

            # create the sounddevice output stream for playback
            self.sdStream = sd.OutputStream(
               samplerate=self.sampleRate,
               blocksize=self.chunkSize,
               channels=self.numChannels,
               callback=self.audioCallback,
               finished_callback=self.onPlaybackFinished
            )

            # start the sounddevice output stream
            self.sdStream.start()
            self.isPlaying = True
            self.playbackEndedNaturally = False   # reset this flag as we are starting

         except Exception as e:   # sounddevice stream did not start
            print(f"Error starting sounddevice stream: {e}")
            self.isPlaying = False

            if self.sdStream:
               self.sdStream.close() # ensure cleanup if start failed
            self.sdStream = None

            # do not re-raise here, allow AudioSample to handle or log
            return   # exit since stream failed to start
            # TODO: rewrite to avoid early return

         if startAtBeginning and self.isPlaying:   # check isPlaying again in case it was set by new stream
            self.isApplyingFadeIn = True
            self.fadeInFramesProcessed = 0


   def onPlaybackFinished(self):
      # NOTE: This callback is called when the stream is stopped or aborted.
      # self.isPlaying = False # Stream is already stopped, this reflects state
      # Don't reset looping here, it's a persistent setting.
      # Don't reset playbackPosition here, might be needed for resume or query.

      # close the sounddevice stream if it exists and is not already closed
      if self.sdStream and not self.sdStream.closed:

         try:   # handle possible exceptions during stream closure (e.g., at interpreter exit)
            self.sdStream.close()   # close the stream to release audio resources

         except sd.PortAudioError as pae:

            if pae.args[1] == sd.PaErrorCode.paNotInitialized:
               pass   # portaudio already terminated, which is expected during atexit

            else:
               print(f"PortAudioError closing stream: {pae}")

         except Exception as e:
            print(f"Generic error closing PortAudio stream: {e}")

      self.sdStream = None   # clear the stream reference after closing

      # Now, if it was a fade out to stop, the isPlaying should already be false.
      # If it stopped for other reasons (e.g. error, or CallbackStop raised not due to fade),
      # ensure isPlaying is False.
      # However, self.isPlaying is primarily controlled by play() and stop() and callback logic.
      # this finished_callback is more for resource cleanup.


   def getLoopsPerformed(self):
      return self.loopsPerformed  # number of loops completed


   def stop(self, immediate=False):
      """
      Stops audio playback with optional immediate termination.

      This method provides two stopping modes: immediate (instant stop) and gradual
      (fade-out stop). The method handles cleanup of audio streams, resets playback
      state variables, and manages fade transitions appropriately.
      """

      # handle case where already stopped (but may have pending fade-out)
      if not self.isPlaying and not self.isApplyingFadeOut:

         # ensure stream is actually closed if somehow isPlaying is False but stream exists
         if self.sdStream and not self.sdStream.closed:

            try:
               self.sdStream.close()   # close the audio stream

            except sd.PortAudioError as pae:

               if pae.args[1] == sd.PaErrorCode.paNotInitialized:
                  pass   # ignore if PortAudio already terminated

               else:
                  print(f"Error closing PyAudio stream: {pae}")

            except Exception as e:
               print(f"Generic error closing PyAudio stream: {e}")

            finally:
               self.sdStream = None   # clear stream reference

         # reset all playback state variables
         self.isPlaying = False   # confirm stopped state
         self.targetEndSourceFrame = -1.0   # reset end frame target
         self.playDurationSourceFrames = -1.0   # reset duration tracking

         # reset loop attributes on stop
         self.loopRegionStartFrame = 0.0   # reset loop start to beginning
         self.loopRegionEndFrame = -1.0   # reset loop end to no loop
         self.loopCountTarget = -1 if self.looping else 0   # reset to constructor state
         self.loopsPerformed = 0   # reset loop counter
         return   # done, since already stopped
         # TODO: rewrite without early return

      # handle immediate stop (skip fade-out for instant termination)
      if immediate:
         # immediately signal all playback logic to stop
         self.isPlaying = False   # signal callback to stop producing audio
         self.isApplyingFadeIn = False   # cancel any ongoing fade-in
         self.isApplyingFadeOut = False   # cancel any ongoing fade-out (e.g. from pause)
         self.isFadingOutToStop = False   # ensure fade-out-to-stop is reset

         # handle immediate stream termination
         if self.sdStream:

            try:
               # check if stream is active before trying to stop

               if not self.sdStream.stopped:
                  self.sdStream.stop()   # stop the PortAudio stream immediately

               # re-check self.sdStream because .stop() could have called _onPlaybackFinished
               # which sets self.sdStream to None

               if self.sdStream and not self.sdStream.closed:
                  self.sdStream.close()   # close and release resources

            except sd.PortAudioError as pae:

               if pae.args[1] == sd.PaErrorCode.paNotInitialized:
                  pass   # PortAudio already terminated, expected during atexit or rapid stop/close

               else:
                  print(f"PortAudioError during immediate stream stop/close: {pae}")

            except Exception as e:
               print(f"Error during immediate stream stop/close: {e}")

            finally:
               self.sdStream = None   # discard stream instance

         # reset all playback state variables for immediate stop
         self.targetEndSourceFrame = -1.0       # reset end frame target
         self.playDurationSourceFrames = -1.0   # reset duration tracking
         self.loopRegionStartFrame = 0.0        # reset loop start to beginning
         self.loopRegionEndFrame = -1.0         # reset loop end to no loop
         self.loopCountTarget = -1 if self.looping else 0   # reset to constructor state
         self.loopsPerformed = 0   # reset loop counter

      else:   # gradual stop (fade out)

         # only start a fade-out if actually playing or was about to start
         if self.isPlaying or self.isApplyingFadeIn:
            self.isApplyingFadeIn = False     # stop any fade-in
            self.isApplyingFadeOut = True     # start fade-out process
            self.isFadingOutToStop = True     # mark that this fade-out is intended to stop playback
            self.fadeOutFramesProcessed = 0   # reset fade-out progress counter
            # isPlaying remains true until fade-out completes in the callback

      # now, the sounddevice stream is stopped


   def close(self):
      self.isPlaying = False   # ensure any playback logic stops

      # cancel any pending fades that might try to operate on a closing stream
      self.isApplyingFadeIn = False
      self.isApplyingFadeOut = False
      self.isFadingOutToStop = False

      if self.sdStream:

         try:
            # check if stream is active before trying to stop
            if not self.sdStream.stopped:
               self.sdStream.stop()   # stop stream activity

            # re-check because .stop() could have called onPlaybackFinished
            if not self.sdStream.closed:
               self.sdStream.close()   # release resources

         except sd.PortAudioError as pae:

            # if PortAudio is already uninitialized (e.g. during atexit), these calls can fail.
            if pae.args[1] == sd.PaErrorCode.paNotInitialized:   # paNotInitialized = -10000
               pass   # suppress error if PortAudio is already down

            else:
               print(f"PortAudioError during stream stop/close: {pae}")
               # raise... # optionally re-raise if it's a different PortAudio error
         finally:
            self.sdStream = None


   def __del__(self):
      # call close() to ensure resources are released
      self.close()
