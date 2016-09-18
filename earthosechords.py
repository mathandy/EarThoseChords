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

try:
    input = raw_input
except: 
    pass

# So user doesn't have to press enter (N/A in progression mode)
from getch import getch  


# External Dependencies
import argparse, time, sys, random, os
from mingus.midi import fluidsynth
from mingus.core import progressions, intervals, chords as ch
import mingus.core.notes as notes
from mingus.containers import NoteContainer, Note


# Octaves possible to use with soundfont 
# Note: leave a buffer of one octave on each side
octaves = range(1, 8)  # if many_octaves flag invoked
DEFAULT_IOCTAVE = 4

# User Arguments
def get_user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-k', '--key',
        default="C",
        help="The key (defaults to C).  Use -m to specify minor key.",
        )

    parser.add_argument(
        '-m', '--minor',
        action='store_true',
        default=False,
        help="If this flag is included, the minor key will be used."
        )

    parser.add_argument(
        '-o', '--many_octaves',
        action='store_true',
        default=False,
        help='If this flag is included, octaves 1-7 will be used.'

        )
    parser.add_argument(
        '-s', '--sevenths',
        action='store_true',
        default=False,
        help='If this flag is included, sevenths will be used instead of triads.'
        )

    parser.add_argument(
        '-f', '--sound_font',
        action='store_true',
        default=os.path.join(os.path.dirname(__file__), "fluid-soundfont", "FluidR3 GM2-2.SF2"),
        help=("You can use this flag to specify a sound font (.sf2) file. " 
              "By default ")
        )

    parser.add_argument(
        '-d', '--delay',
        action='store_true',
        default=1.0,
        help=("Use this flag to specify the delay between chords.")
        )

    return parser.parse_args()


def play_progression(prog, key, octaves=None, Ioctave=4, delay=1.0, Iup = "I"):
    """ Converts a progression to chords and plays them using fluidsynth.
    Iup will be played an octave higher than other numerals by default.
    Set Ioctave to fall for no octave correction from mingus default behavior."""
    if octaves:
        assert len(prog) == len(octaves)

    if not octaves:
        I_chd = NoteContainer(progressions.to_chords([I], key)[0])
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


def resolve(note, key, root=False, mode=None, delay=1.0):
    if mode:
        raise Exception("Not Implimented")

    if not isinstance(note, Note):
        note = Note(note)
    if not isinstance(key, Note):
        key = Note(key)


    num = notes.note_to_int(note.name) - notes.note_to_int(key.name)
    res = []
    if root:
        res.append(num)
    if num % 12 == 0:  # P8
        pass
    if num % 12 == 1:  # m2
        res += [num - 1]
    if num % 12 == 2:  # M2
        res += [num - 2]
    if num % 12 == 3:  # m3
        res += [num - 1, num - 3]
    if num % 12 == 4:  # M3
        res += [num - 2, num - 4]
    if num % 12 == 5:  # P4
        res += [num - 1, num - 3, num - 5]
    if num % 12 == 6:  # TT
        res += [num + 1, num + 5]
    if num % 12 == 7:  # P5
        res += [num + 2, num + 4, num + 5]
    if num % 12 == 8:  # m6
        res += [num - 1, num + 4]
    if num % 12 == 9:  # M6
        res += [num + 2, num + 3]
    if num % 12 == 10:  # m7
        res += [num - 1, num - 3, num + 2]
    if num % 12 == 11:  # M7
        res += [num + 1]

    for n in res:
        n2p = Note(notes.int_to_note(n % 12))
        if n == notes.note_to_int(key.name) + 12:
            n2p.octave = note.octave + 1
        elif notes.note_to_int(n2p.name) < notes.note_to_int(key.name):
            n2p.octave = note.octave + 1
        else:
            n2p.octave = note.octave

        fluidsynth.play_Note(n2p)
        time.sleep(delay)
    return res


def resolve_with_chords(num2res, key, Ioctave):
    """"Note: only relevant for major scale triads."""

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
    play_progression(res, key, Ioctave=Ioctave, delay=DELAY, Iup=I)
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


class Option:
    def __init__(self, command, description, function=None, input_description=None):
        self.command = command
        self.description = description
        self.function = function
        if not input_description:
            self.input_description = command
        else:
            self.input_description = input_description


if __name__ == '__main__':
    # Initialize
    user_args = get_user_args()
    if user_args.sound_font:
        fluidsynth.init(user_args.sound_font)
    else:
        try:
            fluidsynth.init(sf2_em6)
        except:
            try:
                fluidsynth.init(sf2_ex)
            except:
                try:
                    fluidsynth.init(sf2_ex)
                except:
                    raise("Please specify a sound font (.sf2) file using the "
                          "--sound_font flag.")

    # Change instrument
    # fluidsynth.set_instrument(1, 14)  

    # Setup key and mode
    if user_args.minor:
        KEY = user_args.key.lower()
    else:
        KEY = user_args.key.upper()
    if user_args.sevenths:
        [I, II, III, IV, V, VI, VII] = ["I7", "II7", "III7", "IV7", "V7", "VI7", "VII7"]
    else:
        [I, II, III, IV, V, VI, VII] = ["I", "II", "III", "IV", "V", "VI", "VII"]
    
    CADENCE = [I, IV, V, I]
    numerals = [I, II, III, IV, V, VI, VII]
    if not notes.is_valid_note(KEY):
        print("ATTENTION: User-input key, {}, not valid, using C Major instead.".format(KEY))
        KEY = "C"

    # Other user args
    MANY_OCTAVES = user_args.many_octaves
    DELAY = user_args.delay
    PROGRESSION_MODE = False

    # Other args that should be user-adjustable, but aren't yet
    PROG_LENGTHS = [2, 3]  # Number of strums in a progression
    CHORD_LENGTHS = range(1, max(PROG_LENGTHS) + 1)  # Number of strums per chord
    RESOLVE_WHEN_INCORRECT = True
    RESOLVE_WHEN_CORRECT = True
    
    # Useful definitions
    keys = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'Eb', 'E', 'F', 'F#' , 'G' , 'Ab']

    # Options
    options = [Option("v", "hear the cadence"),
               Option("w", "change the delay between chords"),
               Option("s", "toggle between hearing triads and hearing seventh chords"),
               Option("k", "change the key"),
               Option("o", "toggle between using one octave or many"),
               Option("m", "to arpeggiate chord (not available in progression mode)"),
               Option("p", "switch to random progression mode (experimental)"),
               Option("", "hear the chord or progession again", 
                input_description="Press Enter")]

    def isvalidoption(answer):
        return answer in [opt.command for opt in options]

    # Play the Game!!!
    def intro(cadence=CADENCE, key=KEY):
        print("\n" + "~" * 20 + "\n")

        # List options
        print("Note: At any time enter")
        for option in options:
            print(option.input_description, "to", option.description)
        print("\n" + "-" * 10 + "\n")

        # Display key
        if KEY == KEY.lower():
            print("KEY:", KEY.upper(), "min")
        else:
            print("KEY:", KEY, "Maj")
        print("-" * 10)

        # Play cadence
        play_progression(cadence, KEY, delay=DELAY, Iup=I)
        time.sleep(2*DELAY)
        return


    intro()
    newquestion = True
    while 1:
        correct = False

        ### Choose new chord+octave/Progression #################
        # Single chord mode
        if newquestion and not PROGRESSION_MODE:
            # Pick random chord
            numeral = random.choice(numerals)
            chord = NoteContainer(progressions.to_chords([numeral], KEY)[0])

            # Pick random octave, set chord to octave
            if MANY_OCTAVES:
                octave = random.choice(octaves)
                d = octave - chord[0].octave
                for x in chord:
                    x.octave = x.octave + d

                # Find Ioctave
                dist_to_tonic = (int(chord[0]) - int(Note(KEY))) % 12
                I_root = Note().from_int(int(chord[0]) - dist_to_tonic)
                Ioctave = I_root.octave
            else:
                Ioctave = DEFAULT_IOCTAVE

        # Progession mode
        elif newquestion and PROGRESSION_MODE:
            # Randomize key
            # KEY = random.choice(keys)
            # if random.choice([0, 1]]):  # minor or major
            #     KEY = KEY.lower()
            # print("\n" + "-" * 10 + "\n")
            # if KEY == KEY.lower():
            #     print("KEY:", KEY.upper(), "min")
            # else:
            #     print("KEY:", KEY, "Maj")
            # print("-" * 10)

            # Find random chord progression
            prog_length = random.choice(PROG_LENGTHS)
            prog, prog_strums = random_progression(prog_length, numerals, CHORD_LENGTHS)

        ### Play chord/progression
        if PROGRESSION_MODE:
            play_progression(prog_strums, KEY, Ioctave=Ioctave)
        else:
            play_progression([numeral], KEY, Ioctave=Ioctave)


        ### Request user's answer #################
        newquestion = True
        if PROGRESSION_MODE:
            ans = input("Enter your answer using root note names "
                        "or numbers 1-7 seperated by spaces: ").strip()
        else:
            ans = getch("Enter 1-7 or root of chord: ").strip()



        ### Determine if answer is correct (and respond if in PROGRESSION MODE)
        def evalanswer(answer, numeral_, root_note):
            correct_ = False
            if answer == str(numerals.index(numeral_) + 1):
                correct_ = True
            else:
                try:
                    usr_note_val = int(Note(answer[0].upper() + answer[1:])) % 12
                    correct_note_val = int(Note(root_note)) % 12
                    if usr_note_val == correct_note_val:
                        correct_ = True
                except:
                    pass
            return correct_

        def isvalidnote(answer):
            try: return int(answer) in range(1, 8)
            except: pass

            try: return notes.is_valid_note(answer[0].upper() + answer[1:])
            except: pass

            return False

        if isvalidoption(ans):
            pass
        elif PROGRESSION_MODE:
            try:
                int(ans)
                answers = [x for x in ans]
            except:
                answers = ans.split(" ")
            for i, answer in enumerate(answers):
                try:
                    root = NoteContainer(progressions.to_chords([prog[i]], KEY)[0])[0].name
                    print(evalanswer(answer, prog[i][i], root))
                except IndexError:
                    print("too many answers")
            if len(answers) < len(prog):
                print("too few answers")

            print("Progression:", " ".join(prog_strums))
            print("Correct Answer:", " ".join([str(numerals.index(x) + 1) for x in prog]))
            time.sleep(DELAY)
            continue
        else:
            if isvalidnote(ans):
                if evalanswer(ans, numeral, chord[0].name):
                    print("Yes!", chordname(chord, numeral))
                    if RESOLVE_WHEN_CORRECT:
                        resolve_with_chords(numeral, key=KEY, Ioctave=Ioctave)
                else:
                    print("No!", chordname(chord, numeral))
                    if RESOLVE_WHEN_INCORRECT:
                        resolve_with_chords(numeral, key=KEY, Ioctave=Ioctave)

            else:
                print("User input not understood.  Please try again.")
                newquestion = False
                continue


        ### Other parsing of user's answer ##################
        if ans == "":
            newquestion = False
            continue  # skip delay
        elif ans == "k":
            newkey = input("Enter the desired key, use upper-case for major "
                               "and lower-case for minor (e.g. C or c).\n"
                               "Enter R/r for a random major/minor key.")
            if newkey == 'R':
                KEY = random.choice(keys)
            elif newkey == 'r':
                KEY = random.choice(keys).lower()
            elif notes.is_valid_note(newkey):
                KEY = newkey
            else:
                print("Input key not understood, key unchanged.")
            intro(cadence=CADENCE, key=KEY)
            continue

        elif ans == "w":
            DELAY = float(input("Enter the desired delay time (in seconds): "))
            continue

        elif ans == "s":
            if I == "I7":
                [I, II, III, IV, V, VI, VII] = ["I", "II", "III", "IV", "V", "VI", "VII"]
            else:
                [I, II, III, IV, V, VI, VII] = ["I7", "II7", "III7", "IV7", "V7", "VI7", "VII7"]
                continue

        elif ans == "o":
            MANY_OCTAVES = not MANY_OCTAVES
            continue

        elif ans == "q":
            print("OK, you'll get it next time!", chordname(chord, numeral))
            # fluidsynth.play_NoteContainer(chord)
            # time.sleep(DELAY)
            # resolve(chord[0], key=KEY, delay=DELAY)
            resolve_with_chords(numeral, KEY, Ioctave=Ioctave)

        elif ans == "p":
            PROGRESSION_MODE = not PROGRESSION_MODE
            # intro(cadence=CADENCE, key=KEY)
        elif ans == "v" or ans == "cad" or ans == "cadence":
            intro(cadence=CADENCE, key=KEY)
            fluidsynth.play_NoteContainer(chord)
            newquestion = False
            continue

        # other (single chord mode only) parsing
        elif not PROGRESSION_MODE:
            if ans == "m" and not PROGRESSION_MODE:
                for x in chord:
                    fluidsynth.play_Note(x)
                    time.sleep(DELAY/2)
                newquestion = False
                continue
 
        else:
            print("Command not understood.")
            newquestion = False

        time.sleep(DELAY)



