# For python 3 compatibility
from __future__ import division, absolute_import, print_function
try: input = raw_input
except: pass

import settings as st


# External Dependencies
import time, random
from mingus.midi import fluidsynth  # requires FluidSynth is installed
from mingus.core import progressions, intervals, chords as ch
import mingus.core.notes as notes
from mingus.containers import NoteContainer, Note


def random_chord():
    # Pick random chord
    numeral = random.choice(st.NUMERALS)
    chord = NoteContainer(progressions.to_chords([numeral], st.KEY)[0])

    # Pick random octave, set chord to octave   
    if st.MANY_OCTAVES:
        octave = random.choice(st.OCTAVES)
        d = octave - chord[0].octave
        for x in chord:
            x.octave = x.octave + d

        # Find Ioctave
        dist_to_tonic = (int(chord[0]) - int(Note(st.KEY))) % 12
        I_root = Note().from_int(int(chord[0]) - dist_to_tonic)
        Ioctave = I_root.octave
    else:
        Ioctave = st.DEFAULT_IOCTAVE
    return numeral, chord, Ioctave

    
def isvalidnote(answer):
    try:  # return True if response is numerical 1-7
        return int(answer) in range(1, 8)
    except:
        pass
    try:  # return True if response is a valid note name
        return notes.is_valid_note(answer[0].upper() + answer[1:])
    except:
        pass
    return False


def random_key(output_on=True):
    """Returns a random major or minor key.
    Minor in lower case, major in upper case."""
    keys = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab']
    key = random.choice(keys)
    if random.choice([0, 1]):  # minor or major
        key = key.lower()

    # Inform user of new key
    if output_on:
        print("\n" + "-" * 10 + "\n")
        if key == key.lower():
            print("KEY:", key.upper(), "min")
        else:
            print("KEY:", key, "Maj")
        print("-" * 10)

    return key

def play_progression(prog, key, octaves=None, Ioctave=4, delay=1.0, Iup = "I"):
    """ Converts a progression to chords and plays them using fluidsynth.
    Iup will be played an octave higher than other numerals by default.
    Set Ioctave to fall for no octave correction from mingus default behavior."""
    if octaves:
        assert len(prog) == len(octaves)

    if not octaves:
        I_chd = NoteContainer(progressions.to_chords([st.I], key)[0])
        I_chd[0].octave = Ioctave
        I_val = int(I_chd[0])

    chords = []
    for i, numeral in enumerate(prog):

        # find chords from numerals and key
        if numeral == "Iup":
            chord = NoteContainer(progressions.to_chords([Iup], key)[0])
        else:
            chord = NoteContainer(progressions.to_chords([numeral], key)[0])

        # Set octaves
        if octaves:
            d = octaves[i] - chord[0].octave
            for x in chord:
                x.octave += d
        elif Ioctave:  # make sure notes are all at least pitch of that 'I' root
            while int(chord[0]) > I_val:
                for x in chord:
                    x.octave_down()
            while int(chord[0]) < I_val:
                for x in chord:
                    x.octave_up()
        if numeral == "Iup":
            for x in chord:
                x.octave_up()

        chords.append(chord)

    for i, chord in enumerate(chords):
        fluidsynth.play_NoteContainer(chord)
        if i != len(chords) - 1:
            time.sleep(delay)


def resolve_with_chords(num2res, key, Ioctave, numerals):
    """"Note: only relevant for major scale triads."""
    [I, II, III, IV, V, VI, VII] = numerals

    resdict = {
        I : [I],
        II : [II, I],
        III : [III, II, I],
        IV : [IV, III, II, I],
        V : [V, VI, VII, "Iup"],
        VI : [VI, VII, "Iup"],
        VII : [VII, "Iup"],
    }

    res = resdict[num2res]
    play_progression(res, key, Ioctave=Ioctave, delay=st.DELAY, Iup=I)
    return res


def chordname(chord, numeral=None):
    s = ""
    if numeral:
        s = numeral + " - "
    s += "  ::  ".join(ch.determine([x.name for x in chord], True))
    s += " -- " + " ".join([x.name for x in chord])
    return s


def random_progression(number_strums, numerals, strums_per_chord=[1]):

    prog_strums = []
    prog = []
    numeral = ""
    while len(prog_strums) < number_strums:

        tmp = random.choice(numerals)
        if tmp != numeral:  # check not same as previous chord
            numeral = tmp
        strums = random.choice(strums_per_chord)

        # not very elegant/musical (i.e. a "jazzy" solution)
        if len(prog) + strums > number_strums:
            strums = number_strums - len(prog)

        prog_strums += [numeral] * strums
        prog += [numeral]
    return prog, prog_strums