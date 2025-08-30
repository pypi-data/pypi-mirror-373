# creativePythonSetup.py
# This script installs CreativePython, and any missing system requirements
# MacOS: Portaudio (installed via Homebrew)
# Win64: None
# Linux: None

import os, platform, shutil, subprocess
import sys, pathlib

debug = True
LOG_PATH = str(pathlib.Path.home() / "Desktop" / "creativepython-install.log")

class SetupError(Exception):
   pass

def _print(text):
   print(f"[CreativePython Setup]: {text}")

def _run(cmd, env=os.environ, log=None, check=True):
   if debug: _print(f"Running: {' '.join(cmd)}")
   result = subprocess.run(
      cmd,
      check=False,
      text=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      env=env
   )

   if log:
      log.write(f"\n$ {' '.join(cmd)}\n")
      if result.stdout: log.write(result.stdout)
      if result.stderr: log.write(f"\n[stderr]\n{result.stderr}")
   if check and result.returncode != 0:
      raise SetupError(f"Command failed: {' '.join(cmd)} (exit {result.returncode})")
   
   return result


def _findHomebrew():
   if debug: _print("Looking for Homebrew...")
   brew = shutil.which("brew")  # check if brew is on PATH

   if not brew:
      if debug: _print("Didn't find Homebrew, checking other locations...")
      # brew not on PATH, so check common install locations
      commonBins = ["/opt/homebrew/bin/brew", "/usr/local/bin/brew"]
      i = 0
      while not brew and i < len(commonBins):
         if os.path.exists(commonBins[i]):  # bin is installed, so add it to PATH
            os.environ["PATH"] = commonBins[i] + os.pathsep + os.environ.get("PATH", "")
            brew = commonBins[i]
         i = i + 1

   if debug:
      if brew: _print(f"Homebrew found at {brew}")
      else: _print("Failed to find Homebrew...")

   return brew


def _installHomebrew():
   if debug: _print("Installing Homebrew...")
   env = dict(os.environ)
   env["NONINTERACTIVE"] = "1"

   _run('/bin/bash', '-c', '"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"', env=env)  # install homebrew

   brew = _findHomebrew()  # and verify installation   
   if not brew:
      raise SetupError("Homebrew installation failed.  Ensure you have internet access and try again.")
   
   if debug: _print("Homebrew installed successfully.")
   return brew


def _isBrewPackageInstalled(package, brew=None):
   if debug: _print(f"Looking for {package}...")
   if not brew: brew = _findHomebrew()

   isInstalled = subprocess.run(
      [brew, "list", "--versions", package],
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL
   ).returncode == 0

   if debug:
      if isInstalled: _print(f"{package} found.")
      else: _print(f"Failed to find {package}...")

   return isInstalled


def _installBrewPackage(package, brew=None):
   if debug: _print(f"Installing {package}...")
   if not brew: brew = _findHomebrew()

   _run([brew, 'update'])            # update Homebrew...
   _run([brew, 'install', package])  # ... and install package

   if not _isBrewPackageInstalled(package):   # verify installation
      raise SetupError(f"{package} installation failed.  Ensure you have internet access and try again.")
   
   if debug: _print(f"{package} installed successfully.")


def _installCreativePython():
   if debug: _print(f"Installing CreativePython... (log: {LOG_PATH})")

   with open(LOG_PATH, "w", encoding="utf-8", errors="replace") as log:
      # find the python interpreter location
      py = sys.executable.replace("pythonw.exe", "python.exe")

      _run([py, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'], log=log, check=False)
      _run([py, '-m', 'pip', 'install', '--user', 'CreativePython'], log=log)

   if debug: _print("CreativePython installed successfully.")

   import music  # import music to trigger soundfont download



if __name__ == "__main__":
   
   if platform.system() == "Darwin":                # check for MacOS...
      brew = _findHomebrew()
      if not brew:                                  # ... check for Homebrew...
         brew = _installHomebrew()                  # ... no, so install it

      if not _isBrewPackageInstalled("portaudio", brew):  # next, check for portaudio ...
         _installBrewPackage("portaudio", brew)           # ... no, so install it

   # now, requirements have been met
   _installCreativePython()
