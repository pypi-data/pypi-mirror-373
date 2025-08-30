from pathlib import Path
from platformdirs import user_data_dir
from pooch import retrieve
import os

APP = "CreativePython"
ORG = "CofC"

SOUNDFONT_NAME = "default.sf2"
CACHE_DIR = Path(user_data_dir(APP, ORG)) / "SoundFonts"
SOUNDFONT_PATH = CACHE_DIR / SOUNDFONT_NAME

SF2_URL = "https://www.dropbox.com/s/xixtvox70lna6m2/FluidR3%20GM2-2.SF2?dl=1"
SF2_SHA256 = "2ae766ab5c5deb6f7fffacd6316ec9f3699998cce821df3163e7b10a78a64066"

##### SOUNDFONTS #####

def _findSoundfont(candidate=None):
   """
   Finds a soundfont 'default.sf2' and returns its location.
   'candidate' can be another path containing the soundfont.
   """
   candidates = []
   soundfontPath = None

   # path as argument?
   if candidate:
      candidates.append(Path(candidate))
   
   # path as environment variable?
   env = os.getenv("CREATIVEPYTHON_SOUNDFONT")
   if env:
      candidates.append(Path(env))

   # default soundfont location
   candidates+= [SOUNDFONT_PATH, Path.home() / "SoundFonts" / SOUNDFONT_NAME]

   # find first valid candidate
   i = 0
   while soundfontPath is None and i < len(candidates):
      c = candidates[i]
      if c and c.exists():
         soundfontPath = str(c)
      i = i + 1

   return soundfontPath


def _downloadSoundfont(destination=SOUNDFONT_PATH):
   """
   Downloads FluidR3 GM2-2 to given destination as 'default.sf2'
   """
   # create parent directory
   destination.parent.mkdir(parents=True, exist_ok=True)
   # download soundfont
   path = retrieve(
      url=SF2_URL,
      known_hash=f"sha256:{SF2_SHA256}",
      progressbar=False,
      fname=destination.name,
      path=str(destination.parent)
   )
   return path


def _installSoundfont():
   soundfontPath = _findSoundfont()
   if not soundfontPath:
      print(f"[CREATIVEPYTHON SETUP]: Downloading MIDI Soundfont...")
      _soundfontPath = _downloadSoundfont()
      print(f"[CREATIVEPYTHON SETUP]: Soundfont downloaded to {_soundfontPath}")

   return _soundfontPath
