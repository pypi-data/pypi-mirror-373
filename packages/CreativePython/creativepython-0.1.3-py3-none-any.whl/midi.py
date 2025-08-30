################################################################################################################
# midi.py       Version 1.0     24-Mar-2025
# Trevor Ritchie, Taj Ballinger, and Bill Manaris
#
################################################################################################################
#
# [LICENSING GOES HERE]
#
################################################################################################################
#
# This module includes functionality to connect to MIDI devices from input and output.
#

import mido
from math import log
from gui import Display, DropDownList, Color
from timer import Timer2
from music import freqToNote
import atexit

# some useful MIDI event constants
ALL_EVENTS = -1        # a special value so we can register a callback for all events
NOTE_ON    = 144       # 0x90 - Note On
NOTE_OFF   = 128       # 0x80 - Note Off
SET_INSTRUMENT = 192   # 0xC0 - Set Instrument (also known as MIDI program/patch change)
CONTROL_CHANGE = 176   # 0xB0 - Control Change
PITCH_BEND = 224       # 0xE0 - Pitch Bend
AFTERTOUCH = 208       # 0xD0 - Aftertouch
POLYTOUCH = 160        # 0xA0 - Polyphonic Aftertouch

# system common and real-time message mappings
SYSTEM_MESSAGE_VALUES = {
   'system_reset': 255,       # 0xFF - System Reset
   'system_exclusive': 240,   # 0xF0 - System Exclusive
   'songpos': 242,            # 0xF2 - Song Position Pointer
   'songsel': 243,            # 0xF3 - Song Select
   'tune_request': 246        # 0xF6 - Tune Request
}

REALTIME_MESSAGE_VALUES = {
   'clock': 248,      # 0xF8 - Timing Clock
   'start': 250,      # 0xFA - Start
   'continue': 251,   # 0xFB - Continue
   'stop': 252        # 0xFC - Stop
}

# The MIDI specification stipulates that pitch bend be a 14-bit value, where zero is
# maximum downward bend, 16383 is maximum upward bend, and 8192 is the center (no pitch bend).
PITCHBEND_MIN = 0
PITCHBEND_MAX = 16383
PITCHBEND_NORMAL = 8192

# holds active MidiIn and MidiOut objects (for cleanup)
_activeMidiInObjects  = []
_activeMidiOutObjects = []

# holds notes still on to prevent premature note-off for overlapping notes (only last note-off will be executed)
# - list of tuples to prevent race conditions
notesCurrentlyPlaying = []


#################### MidiIn ##############################
#
# MidiIn is used to receive input from a MIDI device.
#
# This class may be instantiated several times to receive input from different MIDI devices
# by the same program.  Each MidiIn object is associated with a (callback) function to be called
# when a MIDI input event arrives from the corresponding MIDI device.  This function should
# accepts four integer parameters: msgType, msgChannel, msgData1, msgData2.
#
# When instantiating, the constructor brings up a GUI with all available input MIDI devices.
#
# For example:
#
# midiIn = MidiIn()
#
# def processMidiEvent(msgType, msgChannel, msgData1, msgData2):
#   print("MIDI In - Message Type:", msgType, ", Channel:", msgChannel, ", Data 1:", msgData1, ", Data 2:", msgData2)
#
# midiIn.onInput( ALL_EVENTS, processMidiEvent )   # register callback function to handle all input MIDI events
#
class MidiIn:

   def __init__(self, preferredDevice=""):
      """Initialize a MidiIn object for receiving MIDI input from devices."""
      self.preferredDevice = preferredDevice  # remember default choice (if any)

      self.display        = None         # holds selection display for available MIDI devices

      self.waitingToSetup = True         # used to busy-wait until user has selected a MIDI input device
      self.midiDevice = None             # holds MIDI input device asscociated with this instance
      self.midiDeviceName = None         # holds MIDI input device name (text to be displayed)
      self.showIncomingMessages = True   # initialize to show incoming messages by default
      self.eventHandlers = {}            # holds callback functions to be called upon receipt of any input events
                                         # (events are keys, functions are dictionary values)

      # holds mido port object (for internal use only)
      self._port = None

      # prompt the user to connect a MIDI device to this object
      self.selectMidiInput(self.preferredDevice)

      # # and, since above GUI is asynchronous, wait until user has selected a MIDI input device
      # while(self.waitingToSetup):
      #    sleep(0.1)    # sleep for 0.1 second


   def __str__(self):
      return f'MidiIn(preferredDevice = {self.preferredDevice})'

   def __repr__(self):
      return str(self)

   def close(self):
      '''Callback used by Receiver interface to close MIDI input device to free any resources it is using'''
      # close the port if it exists
      if self._port:
         self._port.close()
         self._port = None

      # remove from active list
      if self in _activeMidiInObjects:
         _activeMidiInObjects.remove(self)


   def selectMidiInput(self, preferredDevice=""):
      """ Opens preferred MIDI device for input. If this device does not exist,
          creates display with available input MIDI devices and allows to select one.
      """
      self.preferredDevice = preferredDevice    # remember default choice (if any)

      # get all available input devices
      availablePorts = mido.get_input_names()
      self.inputDevices = {}                    # store device info for user-friendly display

      # build dictionary of available devices
      for port in availablePorts:
         self.inputDevices[port] = port         # in mido we don't need separate info and name

      # check if preferredDevice is available
      if self.preferredDevice in self.inputDevices.keys():
         # yes it is, so select it and open it
         self.openInputDevice(self.preferredDevice)

      else:  # otherwise, create menu with available devices to select
         # # create selection CLI
         # self._displayDeviceSelection()

         # get available input devices
         items = list(self.inputDevices.keys())
         items.sort()

         if len(items) > 0:   # if availabale inputs exist
            # create selection display
            self.display = Display("Select MIDI Input", 400, 125) # display info to user
            self.display.drawLabel('Select a MIDI input device from the list', 45, 30)

            # create drop down list
            deviceDropdown = DropDownList(items, self.openInputDevice)
            self.display.add(deviceDropdown, 40, 50)
            self.display.setColor( Color(124, 201, 251) )   # set color to shade of blue (for input)

         else:   # no available inputs
            print("MidiIn: No available MIDI input devices. Please connect a device.")


   # callback for dropdown list - called when user selects a MIDI device
   def openInputDevice(self, selectedItem):
      """Opens the selected MIDI input device."""
      global _activeMidiInObjects

      try:
         # open selected input device
         print(f'MIDI input device set to "{selectedItem}".')   # let user know
         deviceInfo = self.inputDevices[selectedItem]           # get device info from dictionary

         # store device information
         self.midiDeviceName = selectedItem                     # remember device name (in text)

         # for mido implementation
         self._port = mido.open_input(deviceInfo, callback=self._handleMidiMessage)

         # selection has been made, no longer waiting
         self.waitingToSetup = False

         # close display if it exists
         if self.display:
            self.display.close()   # yes, so close it -- no longer needed

         # register this object in the active list for cleanup
         _activeMidiInObjects.append(self)

      except Exception as e:
         print(f"Error opening MIDI device: {e}")


   # def _cliDeviceSelection(self):
   #    """CLI to select input device."""
   #    if not self.inputDevices:
   #       print("No MIDI input devices found.")
   #       self.waitingToSetup = False
   #       return

   #    print("\nSelect a MIDI input device from the list:")

   #    # create dropdown list of available MIDI input devices
   #    items = list(self.inputDevices.keys())
   #    items.sort()

   #    # display options
   #    for i, device in enumerate(items):
   #       print(f"{i+1}. {device}")

   #    # get user selection
   #    while self.waitingToSetup:
   #       try:
   #          choice = input("\nSelect a MIDI input device (number): ")
   #          idx = int(choice) - 1
   #          if 0 <= idx < len(items):
   #             self.openInputDevice(items[idx])
   #             break
   #          else:
   #             print("Invalid selection. Please try again.")
   #       except ValueError:
   #          print("Please enter a number.")
   #       except Exception as e:
   #          print(f"Error: {e}")


   def onNoteOn(self, function):
      """
      Set up a callback function to handle only noteOn MIDI input events.
      """
      # register the callback for NOTE_ON events
      if NOTE_ON not in self.eventHandlers:
         self.eventHandlers[NOTE_ON] = []

      self.eventHandlers[NOTE_ON].append(function)


   def onNoteOff(self, function):
      """
      Set up a callback function to handle only noteOff MIDI input events.
      """
      # register the callback for NOTE_OFF events
      if NOTE_OFF not in self.eventHandlers:
         self.eventHandlers[NOTE_OFF] = []

      self.eventHandlers[NOTE_OFF].append(function)


   def onSetInstrument(self, function):
      """
      Set up a callback function to handle only setInstrument MIDI input events.
      """
      # register the callback for SET_INSTRUMENT events
      if SET_INSTRUMENT not in self.eventHandlers:
         self.eventHandlers[SET_INSTRUMENT] = []
      self.eventHandlers[SET_INSTRUMENT].append(function)


   def onInput(self, eventType, function):
      """
      Associates an incoming event type with a callback function.  Can be used repeatedly to associate different
      event types with different callback functions (one function per event type).  If called more than once for the
      same event type, only the latest callback function is retained (the idea is that this function can contain all
      that is needed to handle this event type).  If eventType is ALL_EVENTS, the associated callback function is
      called for all events not handled already.
      """
      # register the callback for the specified event type
      if eventType not in self.eventHandlers:
         self.eventHandlers[eventType] = []

      self.eventHandlers[eventType].append(function)


   def showMessages(self):
      """
      Turns on printing of incoming MIDI messages (useful for exploring what MIDI messages
      are generated by a particular device).
      """
      self.showIncomingMessages = True


   def hideMessages(self):
      """
      Turns off printing of incoming MIDI messages.
      """
      self.showIncomingMessages = False


   def send(self, message, timeStamp):
      """Callback used by Receiver interface to handle incoming MIDI messages."""
      # TODO: do we need this for compatibility?
      # in our implementation, messages are handled by _handleMidiMessage
      pass


   def _handleMidiMessage(self, message):
      """Handle incoming MIDI messages and dispatch to registered callbacks."""
      # default values
      msgType = None
      msgChannel = 0
      msgData1 = 0
      msgData2 = 0

      # map mido message types to our constants and extract data
      if message.type == 'note_on':
         msgType = NOTE_ON
         msgChannel = message.channel
         msgData1 = message.note
         msgData2 = message.velocity

         # note_on with velocity 0 is treated as note_off in MIDI spec
         if msgData2 == 0:
            msgType = NOTE_OFF

      elif message.type == 'note_off':
         msgType = NOTE_OFF
         msgChannel = message.channel
         msgData1 = message.note
         msgData2 = message.velocity

      elif message.type == 'program_change':
         msgType = SET_INSTRUMENT
         msgChannel = message.channel
         msgData1 = message.program
         msgData2 = 0

      elif message.type == 'control_change':
         # map control change messages
         msgType = CONTROL_CHANGE
         msgChannel = message.channel
         msgData1 = message.control  # control number (e.g., 7 for volume)
         msgData2 = message.value    # control value

      elif message.type == 'pitchwheel':
         # map pitch bend messages
         msgType = PITCH_BEND
         msgChannel = message.channel

         # mido uses a single value from -8192 to 8191 for pitch bend
         # MIDI uses two 7-bit values: LSB and MSB
         # We need to convert the mido format to MIDI format
         pitch_value = message.pitch + 8192     # convert to 0-16383 range
         msgData1 = pitch_value & 0x7F          # LSB (bits 0-6)
         msgData2 = (pitch_value >> 7) & 0x7F   # MSB (bits 7-13)

      elif message.type == 'aftertouch':
         # map channel pressure (aftertouch) messages
         msgType = AFTERTOUCH
         msgChannel = message.channel
         msgData1 = message.value
         msgData2 = 0

      elif message.type == 'polytouch':
         # map polyphonic aftertouch messages
         msgType = POLYTOUCH
         msgChannel = message.channel
         msgData1 = message.note
         msgData2 = message.value

      # system common messages
      elif message.type == 'sysex':
         # handle system exclusive messages
         msgType = 240  # 0xF0 (240) is sysex
         msgChannel = 0
         msgData1 = 0
         msgData2 = 0
         # NOTE: sysex data would be in message.data but we only handle 4 parameters

      elif message.type.startswith('system_'):
         # MIDI System messages have status bytes in the range 0xF0-0xFF (240-255 in decimal)

         # get the full status byte value for this message type, or default to 240 (0xF0) if not recognized
         msgType = SYSTEM_MESSAGE_VALUES.get(message.type, 240)

         # system messages don't use channels
         msgChannel = 0

         # safely extract data values if they exist in the message
         # some system messages might have data parameters, others don't
         if hasattr(message, 'data1'):
            msgData1 = message.data1

         else:
            msgData1 = 0

         if hasattr(message, 'data2'):
            msgData2 = message.data2

         else:
            msgData2 = 0

      # MIDI real-time messages are single-byte messages used for synchronization
      elif message.type in ('clock', 'start', 'continue', 'stop'):
         # real-time messages have status bytes in the range 0xF8-0xFC (248-252 in decimal)

         # get the status byte value for this real-time message
         msgType = REALTIME_MESSAGE_VALUES.get(message.type, 248)  # default to clock if not recognized

         # real-time messages don't use channels or data bytes
         msgChannel = 0
         msgData1 = 0
         msgData2 = 0

      # if we couldn't map the message type, skip processing
      if msgType is None:
         return

      # print message if enabled
      if self.showIncomingMessages:
         print(f"{self.midiDeviceName} (MidiIn) - Event Type: {msgType}, Channel: {msgChannel}, Data 1: {msgData1}, Data 2: {msgData2}")

      # call event-specific handlers
      if msgType in self.eventHandlers:
         for handler in self.eventHandlers[msgType]:

            try:
               handler(msgType, msgChannel, msgData1, msgData2)

            except Exception as e:
               print(f"Error in event handler: {e}")

      # call general handlers for ALL_EVENTS
      if ALL_EVENTS in self.eventHandlers:
         for handler in self.eventHandlers[ALL_EVENTS]:

            try:
               handler(msgType, msgChannel, msgData1, msgData2)

            except Exception as e:
               print(f"Error in ALL_EVENTS handler: {e}")


#################### MidiOut ##############################
#
# MidiOut is used to send output a MIDI device.
#
# This class may be instantiated several times to send output to different MIDI devices
# by the same program.
#
# When instantiating, the constructor brings up a GUI with all available output MIDI devices.
# You may create several instances, one for every MIDI device you wish to send output to.
# Then, to output a MIDI message, call sendMidiMessage() with 4 parameters: msgType, msgChannel
# msgData1, msgData2.
#
# For example:
#
# midiOut = MidiOut()
#
# noteOn = 144   # msgType for starting a note
# noteOff = 128  # msgType for ending a note
# channel = 0    # channel to send message
# data1 = 64     # for NOTE_ON this is pitch
# data2 = 120    # for NOYE_ON this is velocity (volume)
#
# midiOut.sendMidiMessage(noteOn, channel, data1, data2)  # start note
#
# midiOut.sendMidiMessage(noteOff, channel, data1, data2) # end note
# midiOut.sendMidiMessage(noteOn, channel, data1, 0)      # another way to end note (noteOn with 0 velocity)
#

class MidiOut:

   def __init__(self, preferredDevice=""):
      """Initialize a MidiOut object for sending MIDI output to devices."""

      self.preferredDevice = preferredDevice    # remember default choice (if any)

      self.display        = None       # holds selection display for available MIDI devices

      self.waitingToSetup = True       # used to busy-wait until user has selected a MIDI input device
      self.midiDevice     = None       # holds the selected output MIDI device (we may want to close it)
      self.midiDeviceName = None       # holds MIDI output device name (text to be displayed)

      self._port = None   # holds mido port object (for internal use)

      # initialize per-channel settings
      self.instrument = {}        # holds current instrument for each channel
      self.volume = {}            # holds current global volume
      self.panning = {}           # holds current global panning

      # initialize pitchbend across channels to 0
      self.pitchBend = {}    # holds pitchbend to be used when playing a note / frequency (see below)
      for i in range(16):
         self.pitchBend[i] = 0   # set this channel's pitchbend to zero

      # initialize all channels
      for channel in range(16):
         self.instrument[channel] = 0   # PIANO (default)
         self.volume[channel] = 127     # max volume
         self.panning[channel] = 63     # center panning

      # prompt the user to connect to a MIDI device
      self.selectMidiOutput(self.preferredDevice)

      # # and, since above GUI is asynchronous, wait until user has selected a MIDI output device
      # while(self.waitingToSetup):
      #    sleep(0.1)    # sleep for 0.1 second


   def __str__(self):
      return f'MidiOut(preferredDevice = {self.preferredDevice})'

   def __repr__(self):
      return str(self)

   def close(self):
      '''Close MIDI output device to free any resources it is using.'''
      # first, stop all notes playing
      self.allNotesOff()

      # close the port if it exists
      if self._port:
         self._port.close()
         self._port = None

      # remove from active list
      if self in _activeMidiOutObjects:
         _activeMidiOutObjects.remove(self)


   def play(self, material):
      """Play jMusic material (Score, Part, Phrase, Note) using the MIDI output device."""
      pass


   def noteOn(self, pitch, velocity=100, channel=0, panning = -1):
      """Send a NOTE_ON message for this pitch to the selected output MIDI device.  Default panning of -1 means to
         use the default (global) panning setting of the selected MIDI device."""

      if (type(pitch) == int) and (0 <= pitch <= 127):   # a MIDI pitch?
         # for standard MIDI notes, use the current pitch bend setting
         # if panning is specified, set it
         if panning != -1:
            self.sendMidiMessage(CONTROL_CHANGE, channel, 10, panning)

         # send the note on message with the current pitch bend
         self.sendMidiMessage(NOTE_ON, channel, pitch, velocity)

         # keep track of the note playing (for noteOff)
         noteID = (pitch, channel)
         notesCurrentlyPlaying.append(noteID)

      elif type(pitch) == float:        # a pitch in Hertz?
         self.frequencyOn(pitch, velocity, channel, panning)  # handle microtones

      else:
         print(f"MidiOut.noteOn(): Unrecognized pitch {pitch}, expected MIDI pitch from 0 to 127 (int), or frequency in Hz from 8.17 to 12600.0 (float).")


   def frequencyOn(self, frequency, velocity=100, channel=0, panning = -1):
      """Send a NOTE_ON message for this frequency (in Hz) to the selected output MIDI device.  Default panning of -1 means to
         use the default (global) panning setting of the MIDI device."""
      if (type(frequency) == float) and (8.17 <= frequency <= 12600.0): # a pitch in Hertz (within MIDI pitch range 0 to 127)?

         pitch, bend = freqToNote( frequency )                     # convert to MIDI note and pitch bend

         # also, keep track of how many overlapping instances of this pitch are currently sounding on this channel
         # so that we turn off only the last one - also see frequencyOff()
         noteID = (pitch, channel)              # create an ID using pitch-channel pair
         notesCurrentlyPlaying.append(noteID)   # add this note instance to list

         self.noteOnPitchBend(pitch, bend, velocity, channel, panning)      # and start it

      else:
         print(f"MidiOut.frequencyOn(): Invalid frequency {frequency}, expected frequency in Hz from 8.17 to 12600.0 (float).")


   def noteOff(self, pitch, channel=0):
      """Send a NOTE_OFF message for this pitch to the selected output MIDI device."""

      if (type(pitch) == int) and (0 <= pitch <= 127):   # a MIDI pitch?
         # for standard MIDI notes, send a direct NOTE_OFF message
         noteID = (pitch, channel)

         # check if this note is playing
         if noteID in notesCurrentlyPlaying:
            notesCurrentlyPlaying.remove(noteID)

            # Only send note off if this was the last instance
            if noteID not in notesCurrentlyPlaying:
               self.sendMidiMessage(NOTE_OFF, channel, pitch, 0)

      elif type(pitch) == float:        # a pitch in Hertz?
         self.frequencyOff(pitch, channel)  # handle microtones
      else:
         print(f"MidiOut.noteOff(): Unrecognized pitch {pitch}, expected MIDI pitch from 0 to 127 (int), or frequency in Hz from 8.17 to 12600.0 (float).")


   def frequencyOff(self, frequency, channel=0):
      """Send a NOTE_OFF message for this frequency (in Hz) to the selected output MIDI device."""
      if (type(frequency) == float) and (8.17 <= frequency <= 12600.0): # a frequency in Hertz (within MIDI pitch range 0 to 127)?

         pitch, bend = freqToNote( frequency )                     # convert to MIDI note and pitch bend

         # also, keep track of how many overlapping instances of this frequency are currently playing on this channel
         # so that we turn off only the last one - also see frequencyOn()
         noteID = (pitch, channel)                   # create an ID using pitch-channel pair

         # next, remove this noteID from the list, so that we may check for remaining instances
         notesCurrentlyPlaying.remove(noteID)        # remove noteID
         if noteID not in notesCurrentlyPlaying:     # is this last instance of note?

            # yes, so turn it off!
            self.sendMidiMessage(NOTE_OFF, channel, pitch, 0)
      else:
         # frequency was outside expected range
         print(f"MidiOut.frequencyOff(): Invalid frequency {frequency}, expected frequency in Hz from 8.17 to 12600.0 (float).")


   def note(self, pitch, start, duration, velocity=100, channel=0, panning = -1):
      """Plays a note with given 'start' time (in milliseconds from now), 'duration' (in milliseconds
         from 'start' time), with given 'velocity' on 'channel'.  Default panning of -1 means to
         use the default (global) panning setting of the MIDI output device. """
      # TODO: We should probably test for negative start times and durations (comment from JythonMusic)

      # create a timer for the note-on event
      noteOn = Timer2(start, self.noteOn, [pitch, velocity, channel, panning], False)

      # create a timer for the note-off event
      noteOff = Timer2(start+duration, self.noteOff, [pitch, channel], False)

      # and activate timers (set things in motion)
      noteOn.start()
      noteOff.start()

      # NOTE:  Upon completion of this function, the two Timer objects become unreferenced.
      #        When the timers elapse, then the two objects (in theory) should be garbage-collectable,
      #        and should be eventually cleaned up.  So, here, no effort is made in reusing timer objects, etc.


   def frequency(self, frequency, start, duration, velocity=100, channel=0, panning = -1):
      """Plays a frequency with given 'start' time (in milliseconds from now), 'duration' (in milliseconds
         from 'start' time), with given 'velocity' on 'channel'.  Default panning of -1 means to
         use the default (global) panning setting of the MIDI output device."""
      # NOTE:  We assume that the end-user will ensure that concurrent microtones end up on
      # different channels.  This is needed since MIDI has only one pitch band per channel,
      # and most microtones require their unique pitch bending.
      # TODO: We should probably test for negative start times and durations (comment from JythonMusic)

      # create a timer for the frequency-on event
      frequencyOn = Timer2(start, self.frequencyOn, [frequency, velocity, channel, panning], False)

      # create a timer for the frequency-off event
      frequencyOff = Timer2(start+duration, self.frequencyOff, [frequency, channel], False)

      # call pitchBendNormal to turn off the timer, if it is on
      #setPitchBendNormal(channel)
      # and activate timers (set things in motion)
      frequencyOn.start()
      frequencyOff.start()


   def setPitchBend(self, bend = 0, channel=0):
      """Set global pitchbend variable to be used when a note / frequency is played.
         Per JythonMusic API: Pitch bend ranges from -8192 (max downward bend) to 8191 (max upward bend).
         No pitch bend is 0 (this is the default).
      """
      self.pitchBend[channel] = bend

      # Convert from JythonMusic format (-8192 to 8191) to MIDI format (0-16383)
      # where 8192 is the center (no bend)
      midiBend = bend + PITCHBEND_NORMAL

      # clamp to valid range
      midiBend = max(PITCHBEND_MIN, min(midiBend, PITCHBEND_MAX))

      # NOTE: MIDI data bytes are limited to 7 bits (0-127), but pitch bend requires 14-bit resolution (0-16383)
      # for smooth, precise control. We must split the 14-bit value into two 7-bit parts to transmit it.
      lsb = midiBend & 0x7F          # least significant 7 bits
      msb = (midiBend >> 7) & 0x7F   # most significant 7 bits

      # send the MIDI message
      self.sendMidiMessage(PITCH_BEND, channel, lsb, msb)


   def getPitchBend(self, channel=0):
      """Returns the current pitchbend for this channel."""
      return self.pitchBend[channel]


   def noteOnPitchBend(self, pitch, bend = 0, velocity=100, channel=0, panning = -1):
      """Send a NOTE_ON message for this pitch and pitch bend to the selected output MIDI device.
         Default panning of -1 means to use the default (global) panning setting of the MIDI device."""

      self.setPitchBend(bend, channel)   # send pitch bend message

      # and send the message to start the note on this channel
      if panning != -1:                                               # if we have a specific panning,
         self.sendMidiMessage(CONTROL_CHANGE, channel, 10, panning)   # then, use it (otherwise let default / global panning stand)
         # (see controller numbers - http://www.indiana.edu/~emusic/cntrlnumb.html)

      self.sendMidiMessage(NOTE_ON, channel, pitch, velocity)  # send the message


   def allNotesOff(self):
      """Turns off all notes on all channels."""
      self.allFrequenciesOff()


   def allFrequenciesOff(self):
      """Turns off all frequencies on all channels."""
      for channel in range(16):  # cycle through all channels
         # send "All Notes Off" (control 123) using Control Change message type
         self.sendMidiMessage(CONTROL_CHANGE, channel, 123, 0)

         # also reset pitch bend
         self.setPitchBend(0, channel)


   def stop(self):
      """Stops all MIDI music from sounding."""
      # NOTE:  This could also handle self.note() notes, which may have been
      #        scheduled to start sometime in the future.  For now, we assume that timer.py
      #        (which provides Timer objects) handles stopping of timers on its own.  If so,
      #        this takes care of our problem, for all practical purposes.  It is possible
      #        to have a race condition (i.e., a note that starts playing right when stop()
      #        is called, but a second call of stop() (e.g., double pressing of a stop button)
      #        will handle this, so we do not concern ourselves with it.

      # then, stop all sounding notes
      self.allNotesOff()

      # NOTE: In the future, we may also want to handle scheduled notes through self.note().  This could be done
      # by creating a list of Timers created via note() and looping through them to stop them here.


   def setInstrument(self, instrument, channel=0):
      """Sets 'channel' to 'instrument' for this channel of the output MIDI device."""

      self.instrument[channel] = instrument                          # remember it
      self.sendMidiMessage(SET_INSTRUMENT, channel, instrument, 0)   # and set it
      # (see controller numbers - http://www.indiana.edu/~emusic/cntrlnumb.html)


   def getInstrument(self, channel=0):
      """Gets the current instrument for this channel of the output MIDI device."""
      return self.instrument[channel]


   def setVolume(self, volume, channel=0):
      """Sets the current coarse volume for this channel of the output MIDI device."""
      self.volume[channel] = volume                               # remember it
      self.sendMidiMessage(CONTROL_CHANGE, channel, 7, volume)    # and set it (7 is controller number for global / main volume)
      # (see controller numbers - http://www.indiana.edu/~emusic/cntrlnumb.html)


   def getVolume(self, channel=0):
      """Gets the current coarse volume for this channel of the output MIDI device."""
      return self.volume[channel]


   def setPanning(self, panning, channel=0):
      """Sets the current panning setting for this channel of the output MIDI device."""
      self.panning[channel] = panning                              # remember it
      self.sendMidiMessage(CONTROL_CHANGE, channel, 10, panning)   # then, use it (otherwise let default / global panning stand)
      # (see controller numbers - http://www.indiana.edu/~emusic/cntrlnumb.html)


   def getPanning(self, channel=0):
      """Gets the current panning setting for this channel of the output MIDI device."""
      return self.panning[channel]


   ####### function to output MIDI message through selected output MIDI device ########
   def sendMidiMessage(self, msgType, msgChannel, msgData1, msgData2):
      """Send a MIDI message with the given parameters."""
      try:
         # map numeric message types to mido message types
         if msgType == NOTE_ON:  # Note On
            msg = mido.Message('note_on', channel=msgChannel, note=msgData1, velocity=msgData2)

         elif msgType == NOTE_OFF:  # Note Off
            msg = mido.Message('note_off', channel=msgChannel, note=msgData1, velocity=msgData2)

         elif msgType == SET_INSTRUMENT:  # Set Instrument (Program Change)
            msg = mido.Message('program_change', channel=msgChannel, program=msgData1)

         elif msgType == CONTROL_CHANGE:  # Control Change
            msg = mido.Message('control_change', channel=msgChannel,
                              control=msgData1, value=msgData2)

         elif msgType == PITCH_BEND:  # Pitch Bend
            # The MIDI spec for pitch bend has: data1 = LSB (bits 0-6) and data2 = MSB (bits 7-13)
            # Combine the values: (MSB << 7) + LSB gives us 0-16383
            fourteenBitValue = (msgData2 << 7) + msgData1

            # mido, like JythonMusic, expects -8192 to 8191, where 0 is center (no bend)
            bendValue = fourteenBitValue - PITCHBEND_NORMAL

            msg = mido.Message('pitchwheel', channel=msgChannel, pitch=bendValue)

         elif msgType == AFTERTOUCH:  # Aftertouch
            msg = mido.Message('aftertouch', channel=msgChannel, value=msgData1)

         elif msgType == POLYTOUCH:  # Poly Aftertouch
            msg = mido.Message('polytouch', channel=msgChannel, note=msgData1, value=msgData2)

         # System Common messages
         elif msgType == SYSTEM_MESSAGE_VALUES['system_exclusive']:  # System Exclusive (SysEx)
            # For SysEx, data1 and data2 are usually just the first bytes of data
            # In a full implementation, this would take a variable-length array
            msg = mido.Message('sysex', data=[msgData1, msgData2])

         elif msgType == SYSTEM_MESSAGE_VALUES['songpos']:  # Song Position Pointer
            # combines two 7-bit values to form a 14-bit value
            position = (msgData2 << 7) + msgData1
            msg = mido.Message('songpos', pos=position)

         elif msgType == SYSTEM_MESSAGE_VALUES['songsel']:  # Song Select
            msg = mido.Message('songsel', song=msgData1)

         elif msgType == SYSTEM_MESSAGE_VALUES['tune_request']:  # Tune Request
            msg = mido.Message('tune_request')

         elif msgType == SYSTEM_MESSAGE_VALUES['system_reset']:  # System Reset
            msg = mido.Message('reset')

         # MIDI Realtime messages
         elif msgType == REALTIME_MESSAGE_VALUES['clock']:  # Timing Clock
            msg = mido.Message('clock')

         elif msgType == REALTIME_MESSAGE_VALUES['start']:  # Start
            msg = mido.Message('start')

         elif msgType == REALTIME_MESSAGE_VALUES['continue']:  # Continue
            msg = mido.Message('continue')

         elif msgType == REALTIME_MESSAGE_VALUES['stop']:  # Stop
            msg = mido.Message('stop')

         else:
            print(f"Unsupported MIDI message type: {msgType}")
            return

         # send the message if we have a port
         if self._port:
            self._port.send(msg)

      except Exception as e:
         print(f"Error sending MIDI message: {e}")


   ####### helper functions ########

   def selectMidiOutput(self, preferredDevice=""):
      """ Opens preferred MIDI device for output. If this device does not exist,
          creates display with available output MIDI devices and allows to select one.
      """
      self.preferredDevice = preferredDevice    # remember default choice (if any)

      # get all available output devices
      availablePorts = mido.get_output_names()
      self.outputDevices = {}                   # store device info for user-friendly display

      # build dictionary of available devices
      for port in availablePorts:
         self.outputDevices[port] = port        # in mido we don't need separate info and name

      # check if preferredDevice is available
      if self.preferredDevice in self.outputDevices.keys():
         # yes it is, so select it and open it
         self.openOutputDevice(self.preferredDevice)

      else:  # otherwise, create menu with available devices to select
         # # create selection GUI
         # self._cliDeviceSelection()

         # get available output devices
         items = list(self.outputDevices.keys())
         items.sort()

         if len(items) > 0:   # if available outputs exist
            # create selection display
            self.display = Display("Select MIDI Output", 400, 125) # display info to user
            self.display.drawLabel('Select a MIDI output device from the list', 45, 30)

            # create drop down list
            deviceDropdown = DropDownList(items, self.openOutputDevice)
            self.display.add(deviceDropdown, 40, 50)
            self.display.setColor( Color(255, 153, 153) )   # set color to shade of red (for output)

         else:   # no available outputs
            print("MidiOut: No available MIDI output devices.")


   # callback for dropdown list
   def openOutputDevice(self, selectedItem):
      """Opens the selected MIDI output device."""
      global _activeMidiOutObjects

      try:
         # open selected output device
         print(f'MIDI output device set to "{selectedItem}".')   # let user know
         deviceInfo = self.outputDevices[selectedItem]           # get device info from dictionary

         # store device information
         self.midiDeviceName = selectedItem                      # remember device name (in text)

         # for mido implementation
         self._port = mido.open_output(deviceInfo)

         # selection has been made, no longer waiting
         self.waitingToSetup = False

         # close display if it exists
         if self.display:
            self.display.close()   # yes, so close it -- no longer needed

         # register this object in the active list for cleanup
         _activeMidiOutObjects.append(self)

      except Exception as e:
         print(f"Error opening MIDI device: {e}")


   # def _cliDeviceSelection(self):
   #    """CLI to select output device."""
   #    if not self.outputDevices:
   #       print("No MIDI output devices found.")
   #       self.waitingToSetup = False
   #       return

   #    print("\nSelect a MIDI output device from the list:")

   #    # create dropdown list of available MIDI output devices
   #    items = list(self.outputDevices.keys())
   #    items.sort()

   #    # display options
   #    for i, device in enumerate(items):
   #       print(f"{i+1}. {device}")

   #    # get user selection
   #    while self.waitingToSetup:
   #       try:
   #          choice = input("\nSelect a MIDI output device (number): ")
   #          idx = int(choice) - 1
   #          if 0 <= idx < len(items):
   #             self.openOutputDevice(items[idx])
   #             break
   #          else:
   #             print("Invalid selection. Please try again.")
   #       except ValueError:
   #          print("Please enter a number.")
   #       except Exception as e:
   #          print(f"Error: {e}")


# function to stop and clean-up all active Midi objects
def _stopActiveMidiObjects():
   """Clean up all active MIDI objects when program is stopped."""
   global _activeMidiInObjects, _activeMidiOutObjects

   # make a copy of lists since we'll be modifying them during iteration
   midiInObjects = _activeMidiInObjects.copy()
   midiOutObjects = _activeMidiOutObjects.copy()

   # close all MidiIn objects
   for midiIn in midiInObjects:
      try:
         # print(f"Closing MIDI input device: {midiIn.midiDeviceName}")
         midiIn.close()
      except Exception as e:
         print(f"Error closing MIDI input device: {e}")

   # close all MidiOut objects
   for midiOut in midiOutObjects:
      try:
         # print(f"Closing MIDI output device: {midiOut.midiDeviceName}")
         # first stop all notes playing
         midiOut.allNotesOff()
         midiOut.close()
      except Exception as e:
         print(f"Error closing MIDI output device: {e}")

   # ensure lists are empty
   _activeMidiInObjects.clear()
   _activeMidiOutObjects.clear()

   # print("All MIDI devices closed.")

# register the cleanup function to be called when the program exits
atexit.register(_stopActiveMidiObjects)

#################### Unit Testing ##############################

if __name__ == '__main__':
   pass
