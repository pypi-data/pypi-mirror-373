################################################################################
# image.py       Version 1.0     30-Jan-2025
# Taj Ballinger, Trevor Ritchie, and Bill Manaris
#
###############################################################################
#
# [LICENSING GOES HERE]
#
###############################################################################
#
#
# REVISIONS:
#     1.0
#
###############################################################################

# the Icon class exists in the gui module, and is fully functional.
# this file is provided for backwards compatibility with JythonMusic.
from gui import *

class Image():

   def __init__(self, filename, height=None):

      if isinstance(filename, str) and height is None:
         self.filename = filename    # store real filename
         self.icon = Icon(filename)  # load image

      elif isinstance(filename, (int, float)) and isinstance(height, (int, float)):
         self.filename = "Image"              # store fake filename
         width = filename                     # argument 'filename' is actually a width
         self.icon = Icon("", width, height)  # create a blank image

      else:
         if height is None:
            raise TypeError(f'Image(): filename must be a string (it was {type(filename)})')
         else:
            raise TypeError(f'Image(): width and height must be numbers (they were {type(filename)}, {type(height)})')
      
      self.display = Display(width=self.icon.getWidth(), height=self.icon.getHeight())
      # self.display.setSize(self.icon.getWidth(), self.icon.getHeight())
      self.display.add(self.icon)

   def __str__(self):
      string = "Image("

      if self.filename == "Image":
         # started with a blank file, so copy width/height
         string += f'filename = {self.getWidth()}, height = {self.getHeight()})'
      else:
         # started with a real filename, so copy that
         string += f'filename = {self.filename})'

      return string

   def __repr__(self):
      return str(self)

   def show(self):
      self.display.show()

   def hide(self):
      self.display.hide()

   def getWidth(self):
      return self.icon.getWidth()

   def getHeight(self):
      return self.icon.getHeight()

   def getPixel(self, col, row):
      return self.icon.getPixel(col, row)

   def setPixel(self, col, row, RGBList):
      self.icon.setPixel(col, row, RGBList)

   def getPixels(self):
      return self.icon.getPixels()

   def setPixels(self, pixels):
      self.icon.setPixels(pixels)

   def write(self, filename):
      self.filename = filename
      self.icon.pixmap.save(filename)



###### Unit Tests ###################################

if __name__ == "__main__":
   pass