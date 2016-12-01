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
from mingus.containers import NoteContainer, Note, Bar


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


class Diatonic(object):
    def __init__(self, key, Ioctave=None):
        self.key = key
        if not Ioctave:
            Ioctave = Note(key).octave
        self.Ioctave = Ioctave

        if key[0] == key[0].lower():  # natural minor
            self.rel_semitones = [0, 2, 3, 5, 7, 8, 10]
            self.keyname = key[0].upper + key[1:] + " Major"
        elif key[0] == key[0].upper():  # major
            self.rel_semitones = [0, 2, 4, 5, 7, 9, 11]
            self.keyname = key + " Minor"
        self.tonic = Note(name=key.upper(), octave=Ioctave)

        self.abs_semitones = [int(self.tonic) + x for x in self.rel_semitones]
        self.notes = [Note().from_int(x) for x in self.abs_semitones]
        self.numdict = dict([(k + 1, n) for k, n in enumerate(self.notes)])

    def relsemi2note(self, rel_semi):
        return Note().from_int(int(self.tonic) + rel_semi)

    def num2note(self, number, ascending=True):
        assert number > 0
        self.rel_semitones[(number - 1) % 8]
        rel_semi = \
            self.rel_semitones[(number - 1) % 8] + 12*((number - 1)//8)
        return self.relsemi2note(rel_semi)

    def relsemi2note(self, rel_semi):
        return Note().from_int(int(self.tonic) + rel_semi)

    def note2num(self, note):
        base_semitones = [x % 12 for x in self.abs_semitones]
        note_base_semi = int(note) % 12
        try:
            return base_semitones.index(note_base_semi) + 1
        except:
            raise ValueError("{} is not a note in {}.".format(note.name, 
                                self.keyname))

    def nums2semidist(self, num1, num2):
        assert 1 <= num1 <= 7
        assert 1 <= num2 <= 7
        return abs(int(self.num2note(num2)) - int(self.num2note(num1)))


    def interval(self, number, root=None, ascending=True):
        assert number > 0
        if not root:
            root = self.notes[0]

        root_num = self.note2num(root)
        if ascending:
            second_note_num = (self.note2num(root) + (number - 1)) % 7
            if second_note_num == 0:
                second_note_num = 7
            semi_dist = self.nums2semidist(root_num, second_note_num)
            if second_note_num < root_num:
                semi_dist = 12 - semi_dist
            second_note_int  = int(root) + semi_dist + 12*((number-1)//7)
        else:
            second_note_num = (self.note2num(root) - (number - 1)) % 7
            if second_note_num == 0:
                second_note_num = 7
            semi_dist = self.nums2semidist(root_num, second_note_num)
            if second_note_num > root_num:
                semi_dist = 12 - semi_dist
            second_note_int  = int(root) - semi_dist - 12*((number-1)//7)

        return NoteContainer(sorted([root, Note().from_int(second_note_int)]))

    def random_note(self):
        return random.choice(self.notes)

    
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


def easy_bar(notes, durations=None):
    _default_note_duration = 4
    if not durations and notes is not None:
        durations = [_default_note_duration]*len(notes)

    # setup Bar object
    bar = Bar()
    if (isinstance(notes, NoteContainer) or 
            isinstance(notes, Note) or notes is None):
        bar.place_notes(notes, _default_note_duration)
    elif notes is None:
        bar.place_notes(notes, _default_note_duration)
    else:
        for x, d in zip(notes, durations):
            bar.place_notes(x, d)
    return bar

def easy_play(notes, durations=None, bpm=None):
    """`notes` should be a list of notes and/or note_containers.
    durations will all default to 4 (quarter notes).
    bpm will default current BPM setting, `st.BPM`."""
    if not bpm:
        bpm = st.BPM
    fluidsynth.play_Bar(easy_bar(notes, durations), bpm=bpm)

def play_wait(duration=4):
    easy_play([None], [duration])

def play_progression(prog, key, octaves=None, Ioctave=4, Iup = "I", bpm=None):
    """ Converts a progression to chords and plays them using fluidsynth.
    Iup will be played an octave higher than other numerals by default.
    Set Ioctave to fall for no octave correction from mingus default behavior.
    """
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

    easy_play(chords, bpm=bpm)


def resolve_with_chords(num2res, key, Ioctave, numerals, bpm=None):
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
    play_progression(res, key, Ioctave=Ioctave, Iup=I, bpm=bpm)
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
        prev_numeral = numeral
        numeral = random.choice(numerals)
        if prev_numeral == numeral:  # check not same as previous chord
            continue

        strums = random.choice(strums_per_chord)

        # not very elegant/musical (i.e. a "jazzy" solution)
        if len(prog) + strums > number_strums:
            strums = number_strums - len(prog)

        prog_strums += [numeral] * strums
        prog += [numeral]
    return prog, prog_strums