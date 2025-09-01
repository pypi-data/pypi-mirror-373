###############################################################################
# timer.py       Version 1.0     20-Aug-2025
# Trevor Ritchie, Taj Ballinger, Drew Smuniewski, and Bill Manaris
#
###############################################################################
#
# [LICENSING GOES HERE]
#
###############################################################################
#
# Timer class for scheduling tasks to run or repeat at fixed time intervals.
#
# REVISIONS:
#
#   1.0     31-Aug-2024 (ds, tb) First implementation.
#
#
# TODO:
#  -
#
###############################################################################

from PySide6.QtWidgets import QApplication
from PySide6.QtCore    import QTimer

############### QT APPLICATION ################################################
# The QApplication object manages PyQt Widgets and their events.
# The .exec() method builds the application, starts the event loop,
# listens for events, and triggers their corresponding handlers.
#
# Once the .exec() method is called, code execution is blocked until the
# application is closed.
# To hide this from the user, we create a delayed call
# to .exec() that triggers when the user's script reaches end of file.
# Other CreativePython libraries that rely on PyQt will use the same QApplication
# object, so we check if it already exists before creating a new one.

# In a typical GUI, the QApplication is created early in the main script,
#  and its .exec() method is called at the end of the program to start
#  the event loop.
# However, we want to allow the user to run and execute scripts dynamically,
#  so we can't call .exec() without occupying the main thread.  Fortunately,
#  Qt has an alternative event loop that runs in a separate thread, but only
#  while the Python interpreter is running.
# To hide the Qt event loop from the user, and allow dynamic scripting, we
#  require the user to run scripts with the -i option, which enables this
#  secondary, hidden event loop, and always makes the interpreter available.

if "_QTAPP_" not in globals():
   _QTAPP_ = None  # claim global variable for QApplication

def _ensureApp():
   """Guarantee that a QApplication is running."""
   # this function is called whenever we create a new display,
   # or queue a function that modifies the display (or the display's items)
   global _QTAPP_
   if _QTAPP_ is None:
      # try to find an existing QApplication instance
      _QTAPP_ = QApplication.instance()
      if _QTAPP_ is None:
         # if no existing QApplication, create a new instance
         _QTAPP_ = QApplication([])
         _QTAPP_.setApplicationName("CreativePython")
         _QTAPP_.setStyleSheet(  # force ToolTip font color to black
            """
            QToolTip {
               color: black;
            }
            """)

# ensure QApplication is created (needed for QTimer)
_ensureApp()


###############################################################################
# Timer
#
# Class for creating a timer (for use to schedule tasks to be executed after
# a given time interval, repeatedly or once).
# Extends Java's Swing Timer.
#
# Methods:
#
# Timer( timeInterval, function, parameters, repeat)
#   Creates a new Timer to call 'function' with 'parameters', after 'timeInterval' (if 'repeat'
#   is True this will go on indefinitely (default); False means once.
#   It uses either Swing's Timer.
#
# start()
#   Starts the timer.
#
# stop()
#   Stops the timer.
#
# isRunning()
#   Returns True if timer is running; False otherwise.
#
# stop()
#   Stops the timer.
#
# setRepeats( flag )
#   Sets the repeat attribute of the timer (True means repeat; False means once).
#####################################################################################

# TODO: do we need this to prevent garbage collection?
# if "_timers" not in globals():
#    _timers = []

class Timer():
   """Timer used to schedule tasks to be run at fixed time intervals."""

   def __init__ (self, timeInterval, function, parameters=[], repeat=True):
      """Specify time interval (in milliseconds), which function to call when the time interval has passed
         and the parameters to pass this function, and whether to repeat (True) or do it only once."""

      # create an internal QTimer
      self._timer = QTimer()

      self.parameters = parameters

      self.setDelay(timeInterval)               # how often should the timer trigger?
      self.setRepeat(repeat)                    # should we do this once or forever?
      self.setFunction(function, parameters)    # register callback function

      self._timer.timeout.connect(self._run)    # connect QTimer timeout signal to our internal run method

      # _timers.append(self)   # add this timer instance to the global timers list

   def __str__(self):
      """Return a string representation of the timer."""
      return f"Timer(timeInterval = {self.getDelay()}, function = {self._function}, parameters = {self.parameters}, repeat = {self.getRepeat()})"

   def __repr__(self):
      """Return the string representation for repr."""
      return str(self)

   def _run(self):
      """Call the user-supplied function with parameters."""
      self._function(*self._parameters)   # call the user-supplied function with parameters

   def start(self):
      """Start the Timer."""
      self._timer.start()   # start the QTimer

   def stop(self):
      """Stop the Timer."""
      self._timer.stop()   # stop the QTimer

   def getDelay(self):
      """Return the timer interval in milliseconds."""
      return self._timer.interval()   # return the timer interval in milliseconds

   def setDelay(self, timeInterval):
      """Set the timer interval."""
      self._timer.setInterval(int(timeInterval))   # set timer interval

      if self.isRunning():
         self._timer.start()   # restart timer if it is already running

   def isRunning(self):
      """Check if the timer is currently active."""
      return self._timer.isActive()   # check if timer is currently active

   def setFunction(self, function, parameters=[]):
      """Set the callback function and its parameters."""
      self._function   = function     # set callback function
      self._parameters = parameters   # set parameters for the callback

   def getRepeat(self):
      """Return true if timer is set to repeat."""
      repeat = not self._timer.isSingleShot()
      return repeat

   def setRepeat(self, repeat):
      """Set the timer to repeat (True) or run once (False)."""
      repeat
      self._timer.setSingleShot(not repeat)   # set the timer to single shot if repeat is false

class Timer2:
   """Custom timer used to schedule tasks to be run at fixed time intervals."""

   def __init__(self, timeInterval, function, parameters=[], repeat=True):
      """Specify time interval (in milliseconds), which function to call when the time interval has passed
         and the parameters to pass this function, and whether to repeat (True) or do it only once."""
      self._interval = timeInterval / 1000.0   # convert ms to seconds to work with Python's Time module
      self._function = function                # callback function to execute
      self._parameters = parameters            # parameters to pass to the callback function
      self._repeat = repeat                    # whether to repeat the timer or run once
      self._scheduled = False                  # flag indicating if timer is scheduled
      self._accumulatedTime = 0                # tracks elapsed time since last execution
      self._running = False                    # flag indicating if timer is currently running

   def __str__(self):
      return f"Timer(timeInterval = {self.getDelay()}, function = {self._function}, parameters = {self._parameters}, repeat = {self.getRepeat()})"

   def __repr__(self):
      return str(self)

   def _tick(self, dt):
      """Internal method called by the ticker thread to update timer state."""
      if not self._running:
         return

      # accumulate the actual elapsed time with high precision
      self._accumulatedTime += dt

      # check if it's time to run the callback
      if self._accumulatedTime >= self._interval:
         # call the function
         self._function(*self._parameters)

         # reset accumulated time, accounting for overshooting
         if self._repeat:
            # DRIFT PREVENTION: subtract exactly one interval, preserving any excess time
            # this is critical for preventing long-term drift in repeated timers
            self._accumulatedTime -= self._interval
         else:
            # for one-shot timers, remove from active timers
            self.stop()

   def start(self):
      """Creates a timer task to perform the desired task as specified (in terms of timeInterval and repeat)."""
      # check if timer is not already running
      if not self._running:
         self._running = True         # set running flag to true
         self._accumulatedTime = 0    # reset accumulated time
         # _timers.append(self)   # add this timer to the active timers list

   def stop(self):
      """Stops scheduled task from executing."""
      # check if timer is currently running
      if self._running:
         self._running = False         # set running flag to false

         # # remove this timer from the active timers list if it exists
         # if self in _timers:
         #    _timers.remove(self)

   def getDelay(self):
      """Returns the delay time interval (in milliseconds)."""
      return self._interval * 1000   # convert back to ms for API consistency

   def setDelay(self, timeInterval):
      """
      Sets a new delay time interval for timer t (in milliseconds).
         This allows to change the speed of the animation, after some event occurs..
      """
      self._interval = timeInterval / 1000.0

      # if running, restart with new interval
      if self.isRunning():
         self.stop()
         self.start()

   def isRunning(self):
      """Returns True if timer is still running, False otherwise."""
      return self._running

   def setFunction(self, function, parameters=[]):
      """Sets the function to execute.  The optional parameter parameters is a list of parameters to pass to the function (when called)."""
      self._function = function
      self._parameters = parameters

   def getRepeat(self):
      """Returns True if timer is set to repeat, False otherwise."""
      return self._repeat

   def setRepeat(self, repeat):
      """Timer is set to repeat if flag is True, and not to repeat if flag is False."""
      self._repeat = repeat

#######################################################################################
# LinearRamp
#
# Creates a linear ramp that calls a function at regular intervals with interpolated values.
# - delayMs: total duration of the ramp in milliseconds
# - startValue: value at the start of the ramp
# - endValue: value at the end of the ramp
# - function: callback function to call with the current interpolated value
# - stepMs: interval between function calls in milliseconds (default: 10)
#
# The ramp will smoothly transition from startValue to endValue over delayMs milliseconds,
# calling the provided function at regular intervals with the current interpolated value.
# The function should accept a single argument representing the current ramp value.
#######################################################################################

class LinearRamp:
   """Creates a linear ramp that calls a function at regular intervals with interpolated values."""

   def __init__(self, delayMs, startValue, endValue, function, stepMs=10):
      """
      Initializes a linear ramp with the given parameters. The ramp will smoothly transition
      from startValue to endValue over delayMs milliseconds, calling the provided function at regular intervals
      (approximately stepMs milliseconds apart) with the current interpolated value.
      The function should accept a single argument representing the current ramp value.
      """
      # remember parameters
      self._delayMs = delayMs
      self._startValue = startValue
      self._endValue = endValue
      self._function = function
      if stepMs <= 0:
         self._stepMs = 10  # default to 10ms if invalid stepMs is provided
      else:
         self._stepMs = stepMs
      self._timer = None
      self._currentStep = 0

      # make sure function is callable
      if not callable(function):   # callbackFunc is not callable, print error and do nothing
         print("LinearRamp: Error - function must be callable.")
         self._numSteps = 0

      else:   # function is callable
         if self._delayMs <= 0:  # zero or negative delay
            self._numSteps = 1   # ensure at least one call to callbackFunc with endValue

         else:   # positive delay
            # calculate number of steps
            self._numSteps = max(1, int(round(self._delayMs / self._stepMs)))

   def start(self):
      """Starts the linear ramp."""

      if self._timer and self._timer.isRunning():   # timer already running, don't start again
         print("LinearRamp: Ramp is already running.")

      elif not callable(self._function):   # callbackFunc is not callable
         # print error and do nothing
         print("LinearRamp: Error - callbackFunc must be callable to start.")

      else:   # all good, so start the ramp
         self._currentStep = 0   # reset step counter

         # handle immediate execution for zero or negative delay
         if self._delayMs <= 0:
            self._rampStep()   # call the callback function immediately
         else:
            # determine the interval for the timer

            if self._numSteps == 1:   # timer should fire once after delayMs.
               timeIntervalMs = self._delayMs

            else:   # otherwise, it fires numSteps times with interval stepMs.
               timeIntervalMs = self._stepMs

            # repeat the timer if there are multiple steps
            shouldRepeat = (self._numSteps > 1)

            # create the timer
            self._timer = Timer2(timeInterval=timeIntervalMs,
                                 function=self._rampStep,
                                 repeat=shouldRepeat)

            # start the timer
            self._timer.start()

   def _rampStep(self):
      """Internal method called by the Timer at each step of the ramp."""

      if self._currentStep < self._numSteps:   # ramp is not complete

         # calculate progress
         if self._numSteps == 1 : # handles delayMs <=0 or very short ramps
            progress = 1.0

         else:   # positive delay
            progress = float(self._currentStep) / (self._numSteps -1)   # ensures last step hits endValue

         # calculate the current value
         currentValue = self._startValue + (self._endValue - self._startValue) * progress

         # call the callback function
         self._function(currentValue)

         # increment the step
         self._currentStep += 1

      else:   # ramp is complete
         self._function(self._endValue)   # ensure final value is called

         if self._timer:   # cleanup timer
            self._timer.stop()
            self._timer = None


############### Timer2 #################################################################
# To work around the limitation that we can't easily schedule callbacks at specific times,
# we create a ticker thread that wakes up at short intervals to check if any timers
# need to be triggered.
#
# ACCURACY ADVANTAGES:
# 1. Running in a separate thread means timing isn't affected by operations in the main thread
# 2. Measuring actual elapsed time (dt) compensates for any processing delays
# 3. Accumulating precise time values prevents long-term drift
#
# Timers are added to _activeTimers when they start, and removed when they stop
# or, if they are oneshots, when they call their callback function.

# global ticker thread that calls timer callbacks

import threading, time, atexit

def _tickerThread():
   """Internal function that periodically updates all active timers.

   This function runs in a separate thread and wakes up at regular intervals
   to call the _tick method of all active timers. It measures the actual time
   elapsed between calls to ensure timing accuracy.
   """

   lastTime = time.time()
   while _tickerRunning:
      currentTime = time.time()
      dt = currentTime - lastTime  # measure actual elapsed time between ticks
      lastTime = currentTime

      # call tick for all active timers with the precise time difference
      for timer in list(_activeTimers):
         timer._tick(dt)

      # sleep for a short time (adjust as needed for precision)
      time.sleep(0.01)  # 10ms resolution - balances CPU usage with timing precision

# if this is the first time loading this module, initialize global variables
_initialized = False
if not _initialized:
   _initialized = True
   _activeTimers = []
   _tickerRunning = True

   # allow Python to exit even if thread is running
   _ticker = threading.Thread(target=_tickerThread, daemon=True)

   # start ticker thread
   _ticker.start()

   # NOTE: We don't need a blocking thread when using python -i,
   # since the interpreter stays open already

   # register cleanup on exit
   def _cleanup():
      """Cleans up all active timers when the program exits.

      This function is registered with atexit to ensure proper cleanup
      even if the program terminates unexpectedly.
      """
      global _tickerRunning
      _tickerRunning = False

      # stop all active timers
      for timer in list(_activeTimers):
         timer.stop()

   atexit.register(_cleanup)


class Timer2:
   """Timer used to schedule tasks to be run at fixed time intervals."""

   def __init__(self, timeInterval, function, parameters=[], repeat=True):
      """Specify time interval (in milliseconds), which function to call when the time interval has passed
         and the parameters to pass this function, and whether to repeat (True) or do it only once."""
      self._interval = timeInterval / 1000.0   # convert ms to seconds to work with Python's Time module
      self._function = function                # callback function to execute
      self._parameters = parameters            # parameters to pass to the callback function
      self._repeat = repeat                    # whether to repeat the timer or run once
      self._scheduled = False                  # flag indicating if timer is scheduled
      self._accumulatedTime = 0                # tracks elapsed time since last execution
      self._running = False                    # flag indicating if timer is currently running

   def __str__(self):
      return f"Timer: {self.getDelay()} ms, repeat: {self.getRepeat()}"

   def __repr__(self):
      return str(self)

   def _tick(self, dt):
      """Internal method called by the ticker thread to update timer state."""
      if not self._running:
         return

      # accumulate the actual elapsed time with high precision
      self._accumulatedTime += dt

      # check if it's time to run the callback
      if self._accumulatedTime >= self._interval:
         # call the function
         self._function(*self._parameters)

         # reset accumulated time, accounting for overshooting
         if self._repeat:
            # DRIFT PREVENTION: subtract exactly one interval, preserving any excess time
            # this is critical for preventing long-term drift in repeated timers
            self._accumulatedTime -= self._interval
         else:
            # for one-shot timers, remove from active timers
            self.stop()

   def start(self):
      """Creates a timer task to perform the desired task as specified (in terms of timeInterval and repeat)."""
      # check if timer is not already running
      if not self._running:
         self._running = True         # set running flag to true
         self._accumulatedTime = 0    # reset accumulated time
         _activeTimers.append(self)   # add this timer to the active timers list

   def stop(self):
      """Stops scheduled task from executing."""
      # check if timer is currently running
      if self._running:
         self._running = False         # set running flag to false
         # remove this timer from the active timers list if it exists
         if self in _activeTimers:
            _activeTimers.remove(self)

   def getDelay(self):
      """Returns the delay time interval (in milliseconds)."""
      return self._interval * 1000   # convert back to ms for API consistency

   def setDelay(self, timeInterval):
      """
      Sets a new delay time interval for timer t (in milliseconds).
         This allows to change the speed of the animation, after some event occurs..
      """
      self._interval = timeInterval / 1000.0

      # if running, restart with new interval
      if self.isRunning():
         self.stop()
         self.start()

   def isRunning(self):
      """Returns True if timer is still running, False otherwise."""
      return self._running

   def setFunction(self, function, parameters=[]):
      """Sets the function to execute.  The optional parameter parameters is a list of parameters to pass to the function (when called)."""
      self._function = function
      self._parameters = parameters

   def getRepeat(self):
      """Returns True if timer is set to repeat, False otherwise."""
      return self._repeat

   def setRepeat(self, repeat):
      """Timer is set to repeat if flag is True, and not to repeat if flag is False."""
      self._repeat = repeat

# Tests

if __name__ == '__main__':
   import time
   seconds = 0
   startTime = time.time()

   def echoTime():
      global seconds
      current = seconds
      seconds += 1
      print(f"Timed Seconds: {current+1}, Actual Seconds: {time.time()-startTime:.3f}")

   # define timer to count and output elapsed time (in seconds)
   t = Timer(1000, echoTime, [], True)
   t.start()

   # test LinearRamp
   print("\n--- LinearRamp Test (0 to 10 over 2 seconds) ---")
   ramp_start_time = time.time()
   def print_ramp_value(value):
      print(f"Ramp Value: {value:.2f} at {time.time() - ramp_start_time:.3f}s")

   # Ramp from 0 to 10 over 2 seconds, with steps approx every 200ms
   ramp = LinearRamp(delayMs=2000, startValue=0, endValue=10, function=print_ramp_value, stepMs=200)
   ramp.start()
