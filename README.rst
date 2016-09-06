EarThoseChords
============

EarThoseChords is a tool to help musicians learn to recognized the root of chords based on it's distance from the tonic of the key.  The motivation for this code came from the success the author has had learning melodic dictation using Alain Benbassat's method as found in the Android App "Functional Ear Trainer" by Serhii Korchan.  
If you enjoy this software, please consider making a donation to Alain Benbassat on his website www.miles.be.

To Run
------
1. Follow the instructions below to install any prerequisites needed.

2. Download and unzip EarThoseChords.

4. Open a terminal/command-prompt, navigate into the folder containing the "earthosechords.py" file, and enter the following command (without the $).

$ python earthosechords.py

Options
-------
**To change the sound font file (used to produce chord sounds), use the -f flag.**

$ python earthosechords.py -f some_font.sf2

**To see more options, type**
$ man python earthosechords.py 

Note: All options, with the exception of changing the sound font file, are also available through (and listed in) the text-based user interface.

Prerequisites
-------------
-  **python 2.x**
-  **numpy**
-  **scipy**
-  **svgwrite**
-  **svgpathtools**

Setup
-----

**1. Get Python 2.**

Note: If you have a **Mac** or are running **Linux**, you already have Python 2.x.  If you're on **Windows**, go download Python 2 and install it.

**2. Install mingus and sequencer python modules:**

This is easy using pip (which typically comes with Python).  Just open up a terminal/command-prompt and enter the following two commands (without the $).

$ pip install mingus
$ pip install sequencer

**3. Download and install fluidsynth** (from http://www.fluidsynth.org/).

This is easy through a linux/mac package manager.

On Linux:
$ sudo apt-get install fluidsynth

On OS X (assuming you have Homebrew installed):
$ brew install fluidsynth

On Windows:
??? I dunno --  I'd recommend googling "fluidsynth binary" unless you are comfortable compiling the source yourself.  If someone finds an easy way, please let me know and I'll update this.

For Help
--------
Contact me, AndyAPort@gmail.com

Licence
-------

This module is under a MIT License.
