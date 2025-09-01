################################################################################################################
# markov.py     Version 1.6          26-Aug-2025
# Trevor Ritchie, Bill Manaris, David Johnson, and Dana Hughes
#
################################################################################################################
#
# [LICENSING GOES HERE]
#
#################################################################################################################
#
# Creates a markov model (of arbitrary order).  Order is specified at object construction time.
#
# Some Definitions:
#
# First-order (order = 1) means symbol to symbol transition, i.e., bigram probabiities.
# Second-order (order = 2) means pair-symbols to symbol transition, i.e., trigram probabilities.
#
# Two main functions:
#
#    learn(sequence) - extracts n-grams from the list of symbols and updates the model accordingly.
#
#    generate(startSequence) - synthesize a phrase of events, given a starting sequence, using transition
#                              probabilities found in the model.
#
#################################################################################################################
#
# REVISIONS:
# 1.6   26-Aug-2025 (tr)   Brought markov into CreativePython. Add CompositeMarkoveModel class.
#                          Updated dictionary iterations and key views to be python3 compatible.
#
# 1.5   18-Sep-2024 (tr)   Removed self.startSequence. In the past, if no startSequence was provided to
#                          generate(),it would use the original first sequence encountered during learning.
#                          Now, if no startSequence is provided, generate() randomly picks a key from self.model
#                          to start with. Removed analyzeCopeEvents() since it is no longer needed.
#
# 1.4   03-Aug-2022 (bm)   Changed function analyze() to learn() - more meaningful / appropriate.
#                          Also, added default option for startSymbol in generate(), since that's usually the
#                          first symbol in the learning corpus.
#
# Earlier notes:
#
# 1.  Quick and dirty version replaced with a much more memory-efficient version.  Maintains a list of
#     the number of occurrences of each symbol, rather than a list of (possibly duplicate) symbols
#
#     Data Structure summarized below:
#
#     model = { tupleOfSymbols: [ transitionDictionary, totalCount] }
#     transitionDictionary = { transitionSymbol: occuranceCount }
#     totalCount = sum(occuranceCounts)
#
# 2.  Although we support arbitrarily large Markov orders, anything more than 2-3 is perhaps unnecessary for most
#     musical applications.  If a large order is used, the model simply memorizes the piece, as there isn't
#     much variety (alternatives) following a large 'key' (sequence of symbols).
#
# Code adopted from http://code.activestate.com/recipes/194364-the-markov-chain-algorithm/
#

from random import *

class MarkovModel():
   """Creates a markov model of arbitrary order.

      First-order (order = 1) means symbol to symbol transition, i.e., bigram probabilities.
      Second-order (order = 2) means pair-symbols to symbol transition, i.e., trigram probabilities.

      Two main functions:

         learn(sequence) - extracts n-grams from the list of symbols and updates the model accordingly.

         generate(startSequence) - synthesize a phrase of events, given a starting sequence, using transition
                                    probabilities found in the model.
   """

   def __init__(self, order=1):

      self.model = {}             # holds symbol transition probabilities (see Data Structure note above...)

      if order < 1:
         raise NotImplementedError("MarkovModel: Order should be 1 or larger.")
      else:
         self.order = order     # remember this model's order (also see notes above...)


   def clear(self):
      """It reinitializes the markov model."""

      self.model = {}


   def learn(self, listOfSymbols):
      """Extracts n-grams from the list of symbols and updates the model accordingly with the corresponding transitions.
      """
      # We want to remember which symbols may appear at the end of a 'phrase'.
      # Thus, we make the last symbol transition to 'None'.
      # When we are generating from the model, whenever a transition leads us to 'None', we stop.

      previous = listOfSymbols[0:self.order]   # extract first key

      for current in (listOfSymbols[self.order:] + [None]):   # loop through remaining symbols
         self.put(tuple(previous), current)                   # add this transition
         previous = previous[1:] + [current]                  # advance to next tuple



   def put(self, tupleOfSymbols, symbol = None):
      """Adds a transition between 'tupleOfSymbols' and 'symbol' into the model.
      """

      # Each entry in the model consists of a dictionary of next potential symbols, and the total number of
      # occurrences in all next symbols.  If the tuple is not in the model, start a new transition dictionary and total
      # count.

      transitions, total = self.model.get(tupleOfSymbols, [{}, 0])
      transitions[symbol] = transitions.get(symbol, 0) + 1           # Increment this symbol's count
      total = total + 1                                              # Increment the total count
      self.model[tupleOfSymbols] = (transitions, total)              # Reassign these changes to the Markov Model


   def get(self, tupleOfSymbols):
      """Returns a random transition (symbol), given the list of possible transitions from tupleOfSymbols.
         It assumes that tupleOfSymbols exists in the model; if not, we simply crash (for efficiency, i.e., no error checking/handling)."""

      transitions, total = self.model[tupleOfSymbols]

      symbols = list(transitions.keys())              # Parallel lists of transition symbols
      counts = list(transitions.values())             # and how often they occur

      # Select a random point between 0 and the total count.  Traverse the list, subtracting
      # counts from this selection.  Once the selection is below zero, stop.  This will
      # efficiently select a symbol from the weighted list

      selection = random() * total              # [0, total)
      symbolIndex = 0                           # For indexing purposes while transversing the lists

      while selection > 0:
         symbol = symbols[symbolIndex]
         selection = selection - counts[symbolIndex]
         symbolIndex = symbolIndex + 1

      # symbol now contains a randomly selected symbol from the available lists, biased by
      # its total count.

      return symbol


   def getTransitions(self, tupleOfSymbols):
      """Returns all transitions (symbols), how often they occur (counts) and the total count, as parallel lists, given the list
         of possible transitions from tupleOfSymbols.
         It assumes that tupleOfSymbols exists in the model; if not, we simply crash (for efficiency, i.e., no error checking/handling)."""

      transitions, total = self.model[tupleOfSymbols]

      symbols = list(transitions.keys())              # Parallel lists of transition symbols
      counts = list(transitions.values())             # and how often they occur

      return symbols, counts, total


   def generate(self, startSequence=None):
      """Returns a random sequence of symbols, based on the model's transitions, starting with 'startSequence'.
      """

      # if no startSequence provided, randomly choose a key from the model
      if startSequence == None:
         # TODO?: weighted probabilities based on how many transitions each start sequence has
         allPossibleStartSequences = list(self.model.keys())
         startSequence = choice(allPossibleStartSequences)
         # print("Start sequence = " + str(startSequence))

      # is the start sequence well formatted?
      if len(startSequence) != self.order:
         raise ValueError("Start sequence has length " + str(len(startSequence)) + \
                           ". Its length should be the same as the Markov model's order, "+ str(self.order) +".")

      # generate a random sequence of symbols, based on the model's transitions
      chain = startSequence       # initialize
      key = startSequence
      current = self.get( tuple(key) )   # get first symbol
      #current = choice(self.model[tuple(key)])   # get first symbol

      while current != None:                     # generate until we find a transition to the end-symbol
         # print("chain = chain + [current]" + str(chain) + " + " + str((current)))
         chain = chain + [current]           # add next symbol to output
         key = key[1:] + [current]              # construct next key
         current = self.get( tuple(key) )           # get next symbol
         #current = choice(self.model[tuple(key)])   # get next symbol

      # now, chain contains a random sequence of symbols, based on the model's transitions
      return chain


   def getNumberOfSymbols(self):
      """Return how many symbols are in the Markov model's memory"""

      return len(self.model.keys())


   def getNumberOfTransitions(self):
      """Return how many transitions are in the Markov model's memory"""

      numTransitions = 0
      for i in self.model.values():
         numTransitions = numTransitions + len(i[0].values())

      return numTransitions


   def __str__(self):
      """How we want to appear when treated as a string."""

      # return str(self.model)
      text = ""
      for key, value in self.model.items():
         text = text + str(key) + ":  " + str(value) + "\n"

      return text


##### Composite Markov Model ##########################################################
#
# A composite Markov model is a collection of Markov models of different orders.
# It enhances Markov chain generation by combining the situational benefits of these different orders.
# First-order (order = 1) means symbol-to-symbol transition, i.e., bigram probabilities.
# Second-order (order = 2) means pair-of-symbols-to-symbol transition, i.e., trigram probabilities.
# And so on...
#
# The retrieval mechanism in a composite Markov model plays a crucial role in transition selection during Markov chain generations.
# When adding to a new Markov chain, the model determines the appropriate transition based on its current state and learned data.
# However, higher-order sequences, which capture complex relationships, may not always be available, especially with limited
# historical data or in unfamiliar contexts. To address this limitation, the retrieval mechanism allows the composite Markov model
# to fall back on lower order models to find a transition. It prioritizes higher-order contexts, but gracefully falls back to lower-orders
# if needed, starting a generation even with limited context. In this way, a Markov chain may be built up to eventually work with
# the maximum order model. By prioritizing informed, context-specific transitions while having a fallback options,
# a composite Markov model can produce coherent Markov chains across a range of starting contexts.

class CompositeMarkovModel():

   def __init__(self, maxOrder):
      """
      Creates a composite Markov model, which is a collection of Markov models of different orders.
      The maxOrder specifies the highest order to be created. Then, models for all of the lower orders are created.
      The lowest order model is always order 1. For example, CompositeMarkovModel(3) will create a model for order 3, order 2, and order 1.

      Two main functions:

         learn(sequence) - extracts n-grams from the list of symbols and updates every order model accordingly.

         generate(startSequence) - synthesize a phrase of events, given a starting sequence, using transition
                                 probabilities found in the model. The highest order model is used to generate the first symbol
                                 in the output sequence. If the highest order model does not have a transition for the given context,
                                 the next lower order model is used, and so on, until a transition is found. The generation ends
                                 when a terminal symbol is reached, or the order 1 model fails.
      """

      # check if max order is valid
      if maxOrder < 1:
         raise NotImplementedError("CompositeMarkovModel: Max order should be 1 or larger.")

      else:
         # store max order
         self.maxOrder = maxOrder  # Maximum order of the composite model

      self.allModels = []   # List to hold the Markov models of different orders in the composite model

      # create Markov models to be stored in the composite model, from low to high order
      for order in range(1, maxOrder + 1):
         model = MarkovModel(order)    # Create a Markov model for the current order
         self.allModels.append(model)  # Add the model to the list of all models


   def learn(self, listOfSymbols):
      """
      Trains each Markov model in the composite model with a given sequence of symbols.

      Parameters:
         listOfSymbols (list): A list of symbols to train the model.

      Returns:
         None
      """

      # loop through each of the models in the composite model
      for model in self.allModels:
         # train the current model with the provided symbols
         model.learn(listOfSymbols)


   def get(self, tupleOfSymbols):
      """
      Retrieves a possible next symbol based on the given context (tupleOfSymbols).

      Parameters:
         tupleOfSymbols (tuple): A tuple representing the current context to check for in the model.

      Returns:
         symbol: The next symbol in the sequence or raises a KeyError if no valid transition exists.
      """

      # get number of symbols in the current context
      contextLength = len(tupleOfSymbols)

      # check if context is valid
      if contextLength < 1:
         raise KeyError("CompositeMarkovModel.get(): tupleOfSymbols is empty.")  # raise error for empty context

      if contextLength > self.maxOrder:
         # if context is longer than max order
         # print("CompositeMarkovModel.get(): Context is longer than max order. Chopping off extra symbols")
         tupleOfSymbols = tupleOfSymbols[:self.maxOrder]  # trim context to maximum allowed length
         contextLength = self.maxOrder                    # update context length to max order

      # iteration variable - starts with maximum usable order
      currentOrder = contextLength

      # termination conditions
      nextSymbolFound = False    # true if a next symbol is found
      lowestOrderFailed = False  # true if the lowest order Markov model fails

      # loop through the available orders until a valid symbol is found, or the lowest order fails
      while not nextSymbolFound and not lowestOrderFailed:
         # get model for the current order (order n is stored at index n-1)
         model = self.allModels[currentOrder - 1]
         # slice the context for the current order
         context = tupleOfSymbols[-currentOrder:]

         try:
            nextSymbol = model.get(context)  # get next symbol using the Markov model with randomness
                                             # if no exception, we found a valid next symbol
            lowestOrderFailed = True
            nextSymbolFound = True           # mark that we have successfully found a next symbol

         except KeyError:

            if currentOrder == 1:
               # lowest order model failed - this means generation is complete
               lowestOrderFailed = True
               # print("Order 1 could not find " + str(tupleOfSymbols) + ". Finished.")

            else:
               # decrement the order to try the next lower one
               currentOrder = currentOrder - 1
               nextSymbolFound = False  # reset flag to indicate symbol hasn't been found yet
               # print("Order " + str(model.order) + " could not find " + str(tupleOfSymbols))

         # now, if nextSymbolFound, nextSymbol contains a valid symbol
         #      if lowestOrderFailed, nextSymbol has not been instantiated

      # determine which termination condition to use
      if not nextSymbolFound:
         # raise KeyError if no valid symbol was found ( from markov.py get() )
         raise KeyError

      else:
         # check if next symbol is valid
         # if nextSymbol is not None:
            # print("Order " + str(model.order) + " added " + str(nextSymbol))

         return nextSymbol  # return the found next symbol

   def generate(self, startSequence=None):
      """
      Generates a complete sequence of symbols based on the given starting sequence.

      Parameters:
         startSequence (list): A list of symbols to start the sequence (optional).

      Returns:
         list: The generated sequence as a list.
      """

      # if startSequence is given
      if startSequence is not None:

         if len(startSequence) < 1:
            # print("Start sequence must be at least length 1. Using random start sequence.")
            startSequence = None  # set to None to indicate random start is needed

         elif len(startSequence) > self.maxOrder:
            # print("Start sequence must be at most the length of the max order. Cutting off extra symbols.")
            # cut off extra symbols to fit within the maximum order
            startSequence = startSequence[:self.maxOrder]

      # if no startSequence is given, pick a random start sequence from the highest order model
      if startSequence is None:
         # TODO?: weighted probabilities based on how many transitions each start sequence has
         highestOrderModel = self.allModels[self.maxOrder - 1]       # get the highest order model
         allPossibleStartSequences = list(highestOrderModel.model.keys())  # retrieve all keys in the model dictionary
         startSequence = choice(allPossibleStartSequences)           # randomly choose a start sequence from available keys

      # iteration variables
      chain = list(startSequence)  # initialize chain of symbols to return, starting with the startSequence
      contextLength = len(chain)   # length of current context, which can grow to maxOrder

      # termination conditions
      reachedTerminal = False  # true if terminal symbol is found
      getFailed = False        # true if the get() function fails

      # looping to generate symbols until terminal symbol is reached or a get failure
      while not reachedTerminal and not getFailed:
         # get the most recent symbols added to the chain - create a tuple to pass to get()
         context = tuple(chain[-contextLength:])

         try:
            # get a next symbol from a list of possible transitions, with weighted randomness
            nextSymbol = self.get(context)

         except KeyError:
            # the context does not exist as a key in the model dictionary, so get() fails
            getFailed = True

         if not getFailed:

            # now, nextSymbol contains a tuple or None
            if nextSymbol is None:
               # terminal symbol reached, so generation is complete
               # print("Terminal symbol reached. Generation finished.")
               reachedTerminal = True

            else:   # we have a valid next symbol
               chain.append(nextSymbol)   # so add it to the Markov chain

               # Since we added a new symbol, we may increase the context length
               # if we have not reached the max order.
               if contextLength < self.maxOrder:
                  # increase the length of the context
                  contextLength += 1

      # Now, if reachedTerminal is True, chain contains a valid result
      #      if getFailed is True, chain contains a valid result (possibly just the start sequence)
      return chain


   def isConnected(self, context):
      """
      Checks if there is a connection between the given context and any model order in the composite Markov model.

      Parameters:
         context (tuple): A tuple representing the current context to check for in the model.

      Returns:
         bool: True if there is a connection (i.e., a valid transition for the context) in any model order;
               False otherwise.
      """

      contextLength = len(context)   # length of context

      # check if context length is within valid range
      if contextLength < 1 or contextLength > self.maxOrder:
         return False  # Invalid context length for the model

      # start with highest available order for the context
      currentOrder = min(contextLength, self.maxOrder)

      # iterate over models from highest order down to the lowest
      while currentOrder > 0:
         model = self.allModels[currentOrder - 1]   # get model for the current order
         slicedContext = context[-currentOrder:]    # slice context to fit the current order

         try:
            # attempt to retrieve next symbol for the sliced context
            model.get(slicedContext)
            return True   # connection found

         except KeyError:
            # decrement order to try with the next lower model
            currentOrder -= 1

      # no valid transition found in any model
      return False


##### Tests ###########################################################################

def testMarkovModel():
   order = 1
   markov = MarkovModel(order)    # create a model

   # let's try some tests
   #listOfSymbols = [60]
   listOfSymbols = [69, 67, 64, 62, 60, 63, 62, 60, 62, 60, 61, 57, 60, 50, 57, 57, 5, 55, 51, 52, 54, 56, 57, 58, 45, 52, 59, 60, 64, 69]
   #startSymbol = listOfSymbols[0]
   startSymbol = listOfSymbols[0:order]
   print("Input = ", listOfSymbols)
   print()

   # let's build the model
   markov.learn(listOfSymbols)

   # let's see the model
   print("Model = \n", markov)
   print()

   # let's return the list of transitions from a specific symbol
   #startSymbol = input("Enter start symbol: ")
   #startSymbol = (56,)
   #print "List of transitions and counts are: ", markov.getTransitions(startSymbol)

   # now, let's generate a chain, based on the random model (all proabilities should be more or less equal
   print("Output = ", markov.generate(startSymbol))
   #print "Output = ", markov.generate([3,4])


def testCompositeMarkovModel():
   # test the learn() and generate() functions with different scenarios

   # opening theme of Fur Elise
   testModel = CompositeMarkovModel(2)        # Creates a composite Markov model with max order 2
   testList = [76, 75, 76, 75, 76, 71, 74, 72, 69, -2147483648,
               60, 64, 69, 71, -2147483648, 64, 68, 71,
               72, -2147483648, 64, 76, 75, 76, 75, 76,
               71, 74, 72, 69, -2147483648, 60, 64, 69,
               71, -2147483648, 64, 72, 71, 69]
   testModel.learn(testList)                  # Train the model with the provided list of symbols
   testResult = testModel.generate([76, 75])  # Generate a sequence starting with a specified start sequence
   print("Test result: " + str(testResult) + "\n")

   # startSequence doesn't match learned information
   testModel = CompositeMarkovModel(3)   # model with max order 3
   testList = [76, 75, 76, 75, 76, 71, 74, 72, 69, -2147483648]
   testModel.learn(testList)
   testResult = testModel.generate([54, 60, 70])
   print("Test result: " + str(testResult) + "\n")

   # startSequence partially matches learned information
   testModel = CompositeMarkovModel(3)   # model with max order 3
   testList = [76, 75, 76, 75, 76, 71, 74, 72, 69, -2147483648,
               60, 64, 69, 71, -2147483648, 64, 68, 71, 72, -2147483648]
   testModel.learn(testList)
   testResult = testModel.generate([54, 60, 64])
   print("Test result: " + str(testResult) + "\n")

   # no startSequence provided
   testModel = CompositeMarkovModel(2)   # model with max order 2
   testList = [76, 75, 76, 75, 76, 71, 74, 72, 69, -2147483648,
               60, 64, 69, 71, -2147483648, 64, 68, 71, 72, -2147483648]
   testModel.learn(testList)
   testResult = testModel.generate()
   print("Test result: " + str(testResult) + "\n")


if __name__ == "__main__":
   testMarkovModel()
   # testCompositeMarkovModel()
