###############################################################################
# osc.py       Version 1.0     19-Aug-2025
# Trevor Ritchie, Taj Ballinger, Drew Smuniewski, and Bill Manaris
#
###############################################################################
#
# [LICENSING GOES HERE]
#
###############################################################################
#
# This module provides functionality for Open Sound Control (OSC)
# communication between programs and OSC devices.
#
# REVISIONS:
#
#
###############################################################################

# expose only OscIn and OscOut classes
__all__ = ['OscIn', 'OscOut']


############### IMPORTS #######################################################

from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
from osc4py3 import oscmethod
import atexit
import socket
import time
import sys
import threading


############### GLOBALS #######################################################

_oscStarted = False   # tracks if the main OSC system has been initialized
_activeOscIns = []   # keeps a list of all active OscIn instances for cleanup


#################### OscIn ##############################
#
# OscIn is used to receive messages from OSC devices.
#
# This class may be instantiated several times to create different OSC input objects (servers)
# to receive and handle OSC messages.
#
# The constructor expects the port number (your choice) to listen for incoming messages.
#
# When instantiated, the OscIn object outputs (print out) its host IP number and its port
# (for convenience).  Use this info to set up the OSC clients used to send messages here.
#
# NOTE:  To send messages here you may use objects of the OscOut class below, or another OSC client,
# such as TouchOSC iPhone client (http://hexler.net/software/touchosc).

# The latter is most enabling, as it allows programs to be driven by external devices, such as
# smart phones (iPhone/iPad/Android).  This way you may build arbitrary musical instruments and
# artistic installations.
#
# Picking port numbers:
#
# Each OscIn object requires its own port.  So, pick port numbers not used by other applications.
# For example, TouchOSC (a mobile app for Android and iOS devices), defaults to 8000 for sending OSC messages,
# and 9000 for receiving messages.  In general, any port from 1024 to 65535 may be used, as long as no other
# application is using it.  If you have trouble, try changing port numbers.  The best bet is a port in
# the range 49152 to 65535 (which is reserved for custom purposes).
#
# For example:
#
# oscIn = OscIn( 57110 )          # create an OSC input device (OSC server) on port 57110
#
# def simple(message):            # define a simple message handler (function)
#    print "Hello world!"
#
# oscIn.onInput("/helloWorld", simple)   # if the incoming OSC address is "/helloWorld",
#                                        # call this function.
#
# def complete(message):          # define a more complete message handler
#     address = message.getAddress()
#     args = message.getArguments()
#     print "\nOSC Event:"
#     print "OSC In - Address:", address,   # print the time and address
#     for i in range( len(args) ):          # and any message arguments (all on the same line)
#        print ", Argument " + str(i) + ": " + str(args[i]),
#     print
#
# oscIn.onInput("/.*", complete)   # all OSC addresses call this function
#

allMessages = "*"  # matches all addresses

class OscIn():
   """
   Receives OSC messages on a specified port.

   This class creates an OSC server that listens for incoming messages
   and dispatches them to registered handler functions.
   """

   def __init__(self, port=57110):
      """
      Create an OSC input server on the specified port.
      """
      global _oscStarted, _activeOscIns
      _activeOscIns.append(self)   # add this instance to the list of active OscIn objects for cleanup

      # _stopEvent is a threading.Event used to signal the processing thread to stop
      # it allows for graceful shutdown of the thread
      self._stopEvent = threading.Event()

      if not _oscStarted:
         osc_startup()   # initialize the osc4py3 library system if not already started
         _oscStarted = True   # mark the OSC system as started

      self.port = port
      hostIP = "127.0.0.1"   # default to localhost
      alternativeIPs = []
      try:
         hostname = socket.gethostname()   # get the local machine's hostname
         hostIP = socket.gethostbyname(hostname)   # resolve the hostname to its primary IP address
         # get all IP addresses associated with the hostname
         allIPs = socket.gethostbyname_ex(hostname)[2]
         # filter out the primary IP and loopback if it's not the primary, ensure uniqueness
         # this provides a list of other IPs the server might be reachable on
         alternativeIPs = sorted(list(set(ip for ip in allIPs if ip != hostIP and ip != "127.0.0.1")))
      except socket.gaierror:
         # hostIP remains "127.0.0.1"
         pass # keep hostIP as 127.0.0.1 if hostname resolution fails, e.g., no network connection

      self.ipAddress = hostIP
      self.serverName = f"oscServer_{self.port}"   # create a unique name for this OSC server instance
      # start a UDP server listening on all available network interfaces ("0.0.0.0") on the specified port
      # this allows receiving messages sent to any of the machine's IP addresses on that port
      osc_udp_server("0.0.0.0", self.port, self.serverName)

      print(f'OSC Server started:')
      print(f'Accepting OSC input on IP address {self.ipAddress}, at port {self.port}')
      if alternativeIPs:
         alt_ip_str = ", ".join(alternativeIPs)
         print(f'(Alternative IP addresses: {alt_ip_str})')
      elif self.ipAddress != "127.0.0.1" and "127.0.0.1" in socket.gethostbyname_ex(socket.gethostname())[2]:
         # if primary is not loopback, but loopback is an option, show it.
         print(f'(Alternative IP addresses: 127.0.0.1)')

      print(f'Use this info to configure OSC clients.\n')

      self.showIncomingMessages = True
      # register a default handler to print all incoming messages
      # allMessages ("*") is a wildcard that matches any OSC address
      # self.onInput(allMessages, self._printIncomingMessage) # Removed to avoid interference

      # create and start a new thread that will run the _processingLoop method
      # daemon=True means this thread will exit automatically when the main program exits
      self._processThread = threading.Thread(target=self._processingLoop, daemon=True)
      self._processThread.start()

   def __str__(self):
      return f'OscIn(port = {self.port})'

   def __repr__(self):
      return str(self)

   def onInput(self, oscAddress, function):
      """
      Associate callback 'function' to OSC messages send to 'oscAddress' on this device.  An 'oscAddress'
      looks like a URL, e.g., "/first/second/third".
      """
      # Convert Python-style ".*" (match any sequence) to OSC-style "*" (match any sequence).
      # This allows users to write "/path/.*" and have it interpreted by osc4py3 (which defaults to OSC patterns)
      # as "/path/*". This also maintains compatibility with existing OSC patterns that do not use ".*".
      convertedOscAddress = oscAddress.replace(".*", "*")

      def handler(rawMsg, sourceId):
         # rawMsg is an oscbuildparse.OSCMessage object from the osc4py3 library
         # sourceId contains information about where the message came from (e.g., IP and port)
         address = rawMsg.addrpattern   # get the OSC address from the raw message
         args = rawMsg.arguments      # get the arguments from the raw message
         msg = _OscMessage(address, args)   # create our custom OSCMessage object

         # print message if showIncomingMessages is True
         if self.showIncomingMessages:
            self._printIncomingMessage(msg) # Call the existing print method

         function(msg)   # call the user-provided function with the formatted message

      # register the handler function with the osc4py3 system
      # osc_method links an OSC address pattern to a function that should be called when a message matching that pattern is received
      # argscheme specifies what arguments the handler function expects
      # OSCARG_MESSAGE passes the raw OSC message object
      # OSCARG_SRCIDENT passes information about the source of the message
      osc_method(convertedOscAddress, handler, argscheme=oscmethod.OSCARG_MESSAGE + oscmethod.OSCARG_SRCIDENT)

   def showMessages(self):
      """
      Turns on printing of incoming OSC messages (useful for exploring what OSC messages
      are generated by a particular device).
      """
      self.showIncomingMessages = True

   def hideMessages(self):
      """
      Turns off printing of incoming OSC messages.
      """
      self.showIncomingMessages = False

   def _printIncomingMessage(self, message):
      """
      Default message handler that prints incoming messages.
      """
      if self.showIncomingMessages:
         oscAddress = message.getAddress()
         oscArgs = message.getArguments()

         print(f'OSC In - Address: "{oscAddress}"', end='')

         for i, arg in enumerate(oscArgs):
            if isinstance(arg, str):
               print(f' , Argument {i}: "{arg}"', end='')
            else:
               print(f' , Argument {i}: {arg}', end='')
         print()

   def _processingLoop(self):
      """Continuously calls osc_process() until _stopEvent is set."""
      # this loop is the heart of the OSC message receiving mechanism
      # it runs in a separate thread to avoid blocking the main program flow
      try:
         while not self._stopEvent.is_set():   # continue looping until the stop event is signaled
            osc_process()   # process any pending OSC events (e.g., received messages)
            # sleep for a very short duration to prevent the loop from consuming 100% CPU
            time.sleep(0.001) # prevent busy-waiting
      except Exception as e:
         print(f"[OSC Error] OscIn processing loop on port {self.port} encountered an error: {e}", file=sys.stderr)


####################### OscOut ##############################
#
# OscOut is used to send messages to OSC devices.
#
# This class may be instantiated several times to create different OSC output objects (clients)
# to send OSC messages.
#
# The constructor expects the IP address and port number of the OSC device to which we are sending messages.
#
# For example:
#
# oscOut = OscOut( "localhost", 57110 )   # connect to an OSC device (OSC server) on this computer listening on port 57110
#
# oscOut.sendMessage("/helloWorld")        # send a simple OSC message
#
# oscOut.sendMessage("/itsFullOfStars", 1, 2.3, "wow!", True)   # send a more detailed OSC message
#

class OscOut():
   """
   Sends OSC messages to a specified IP address and port.
   """

   def __init__(self, IP="localhost", port=57110):
      """
      Create an OSC output client targeting the specified IP and port.
      """
      global _oscStarted

      if not _oscStarted:
         osc_startup()   # initialize the osc4py3 library system if not already started
         _oscStarted = True   # mark the OSC system as started

      if IP == "localhost":
         IP = "127.0.0.1"

      self.IP = IP
      self.port = port

      # create a unique name for this OSC client instance
      # this name is used by osc4py3 to identify the communication channel
      self.client = f"oscClient_{self.IP}_{self.port}"

      # configure an OSC UDP client to send messages to the specified IP and port
      # this sets up a channel in osc4py3 for sending messages to the destination
      osc_udp_client(self.IP, self.port, self.client)

   def __str__(self):
      return f'OscOut(IP = {self.IP}, port = {self.port})'

   def __repr__(self):
      return str(self)

   def sendMessage(self, oscAddress, *args):
      """
      Sends an OSC message consisting of the 'oscAddress' and corresponding 'args' to the OSC output device.
      """
      # create an OSC message object using osc4py3's oscbuildparse module
      # the second argument (typetags) is set to None, allowing osc4py3 to automatically determine them from the arguments
      # args is a tuple of arguments to be sent with the message
      message = oscbuildparse.OSCMessage(oscAddress, None, args)
      # send the prepared OSC message to the client channel configured in __init__
      osc_send(message, self.client)


############### OSC MESSAGE ###################################################
# OSCMessage contains the address and arguments for OSC data.
#
# The address is a string that represents the destination of the message,
# and typically looks like an HTTP URL (e.g. "/oscillator/1/frequency").
#
# The arguments are a list of values that are sent along with the address.
# Arguments can be integers, floats, strings, or booleans.
# this class provides a more python-friendly way to work with OSC messages,
# compared to the raw message format used by the osc4py3 library.

class _OscMessage():
   """
   Represents an OSC message with an address pattern and arguments.

   OSC messages consist of an address pattern (like "/synth/frequency")
   and zero or more arguments of various types (int, float, string, boolean).
   this class simplifies creating and accessing parts of an OSC message.
   """

   def __init__(self, oscAddress, *args):
      """
      Create a new OSC message.
      """
      self.oscAddress = oscAddress

      # convert args to list for easier handling
      # this allows flexibility in how arguments are passed to the constructor
      if len(args) == 1 and isinstance(args[0], (list, tuple)):
         self.arguments = list(args[0])   # if a single list/tuple is passed, use it directly
      else:
         self.arguments = list(args)   # otherwise, treat multiple arguments as a list

   def __str__(self):
      return f'OscMessage(oscAddress = {self.oscAddress}, args = {self.arguments})'

   def __repr__(self):
      return str(self)

   def getAddress(self):
      """
      Get the OSC address pattern of this message.
      """
      return self.oscAddress

   def getArguments(self):
      """
      Get the arguments of this message.
      """
      return self.arguments


############### Cleanup ##############################################

def _cleanupOsc():
   """Gracefully stops all OSC processing threads and terminates OSC system."""
   # this function is automatically called when the python program exits
   # it ensures that all OSC resources are released properly
   global _activeOscIns

   # iterate over a copy of the list, as instances might be removed during shutdown
   for instance in list(_activeOscIns):
      # check if the OscIn instance has a processing thread and if it's still running
      if hasattr(instance, '_processThread') and instance._processThread.is_alive():
         instance._stopEvent.set()   # signal the thread to stop its loop
         instance._processThread.join(timeout=2.0)   # wait for the thread to finish, with a timeout

   if _oscStarted:   # check if the OSC system was ever started
      try:
         osc_terminate()   # tell osc4py3 to shut down its internal components
      except Exception as e:
         # this helps in diagnosing issues if the cleanup process itself fails
         print(f"[OSC Cleanup Error] Exception during global osc_terminate(): {e}", file=sys.stderr)

# register _cleanupOsc to be called automatically when the program exits
atexit.register(_cleanupOsc)


############### Tests ##########################################################

def oscTest():
   """
   Test function demonstrating basic usage of the OSC module.
   Creates both an OSC server and client, sends messages, and processes incoming messages.
   """
   oscIn = OscIn()

   def callback(message):
      print("Callback function called!\n")

   oscIn.onInput("/callback", callback)
   oscOut = OscOut()
   oscOut.sendMessage("/callback")
   oscOut.sendMessage("/soManyArgs!", 42, 3.14, "String", True)

if __name__ == '__main__':
   oscTest()
