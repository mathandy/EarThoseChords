"""
Author: Andy Port
Website: https://github.com/mathandy/EarThoseChords
Email: AndyAPort@gmail.com

EarThoseChords is a tool to help musicians learn to 
recognized the root of chords based on it's distance 
from the tonic of the key.  The motivation for this 
code came from the success the author has had learning 
melodic dictation using Alain Benbassat's method (as 
found in the Android App "Functional Ear Trainer" by 
Serhii Korchan).  
If you enjoy this software, please consider making a 
donation to Alain Benbassat on his website www.miles.be

For help, see README file.
"""


# Just in case the prereqs become python 3 compatible some day
from __future__ import division, absolute_import, print_function
try: input = raw_input
except: pass

# Internal Dependencies
from getch import getch
import game_structure as gs

# External Dependencies
import argparse, time, sys, random, os
from mingus.midi import fluidsynth  # requires FluidSynth is installed
from mingus.core import progressions, intervals, chords as ch
import mingus.core.notes as notes
from mingus.containers import NoteContainer, Note


# Modes
def eval_single(usr_ans, question, root_note):
    correct_ = False
    if usr_ans == str(numerals.index(question) + 1):
        correct_ = True
    else:
        try:
            usr_note_val = int(Note(usr_ans[0].upper() + usr_ans[1:])) % 12
            correct_note_val = int(Note(root_note)) % 12
            if usr_note_val == correct_note_val:
                correct_ = True
        except:
            pass
    return correct_


# Play the Game!!!
if __name__ == '__main__':
    # Initialize
    import settings as st # parses command-line user arguments and initializes settings
    fluidsynth.init(st.SOUNDFONT)  # start FluidSynth

    # Change instrument
    # fluidsynth.set_instrument(1, 14)

    # Initialize Game
    from game_modes import game_modes
    st.CURRENT_MODE = game_modes[st.INITIAL_MODE]
    st.CURRENT_MODE.intro()

    while 1:
        st.CURRENT_MODE.new_question()
        time.sleep(st.DELAY)