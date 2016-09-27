# For python 3 compatible
from __future__ import division, absolute_import, print_function
try: input = raw_input
except: pass

from getch import getch
import game_structure as gs
from musictools import (play_progression, random_progression, 
    random_key, isvalidnote, resolve_with_chords, chordname, 
    random_chord)
import settings as st

# External Dependencies
import time, random, sys
from multiprocessing import Process
from mingus.midi import fluidsynth  # requires FluidSynth is installed
from mingus.core import progressions, intervals, chords as ch
import mingus.core.notes as notes
from mingus.containers import NoteContainer, Note


# Decorators
def repeat_question(func):
   def func_wrapper(*args, **kwargs):
       st.NEWQUESTION = False
       return func(*args, **kwargs)
   return func_wrapper


def new_question(func):
   def func_wrapper(*args, **kwargs):
       st.NEWQUESTION = True
       return func(*args, **kwargs)
   return func_wrapper


# Menu Command Actions
@repeat_question
def play_cadence():
    play_progression(st.CADENCE, st.KEY, delay=st.DELAY, Iup=st.I)


@repeat_question
def set_delay():
    st.DELAY = float(input("Enter the desired delay time (in seconds): "))


@new_question
def toggle_triads7ths():
    if st.I == "I7":
        st.I, st.II, st.III, st.IV, st.V, st.VI, st.VII = \
            "I", "II", "III", "IV", "V", "VI", "VII"
    else:
        st.I, st.II, st.III, st.IV, st.V, st.VI, st.VII = \
            "I7", "II7", "III7", "IV7", "V7", "VI7", "VII7"
    st.NUMERALS = st.I, st.II, st.III, st.IV, st.V, st.VI, st.VII


@new_question
def set_key(reset_score=True):
    mes = ("Enter the desired key, use upper-case for major "
           "and lower-case for minor (e.g. C or c).\n"
            "Enter R/r for a random major/minor key.")
    newkey = input(mes)
    keys = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab']
    if newkey == 'R':
        st.KEY = random.choice(keys)
    elif newkey == 'r':
        st.KEY = random.choice(keys).lower()
    elif notes.is_valid_note(newkey):
        st.KEY = newkey
    else:
        print("Input key not understood, key unchanged.")
    st.CURRENT_MODE.intro()
    if reset_score:
        st.COUNT = 0
        st.SCORE = 0


@repeat_question
def toggle_many_octaves():
    st.MANY_OCTAVES = not st.MANY_OCTAVES


@repeat_question
def arpeggiate(invert=False, descending=False, ):

    arpeggiation = [x for x in st.CURRENT_Q_INFO["chord"]]
    if invert:
        arpeggiation = [arpeggiation[i] for i in invert]
    elif descending:
        arpeggiation.reverse()


    for x in arpeggiation:
        fluidsynth.play_Note(x)
        time.sleep(st.DELAY/2)


def change_game_mode(new_mode):
    @new_question
    def _change_mode():
        st.COUNT = 0
        st.SCORE = 0
        st.CURRENT_MODE = game_modes[new_mode]
    return _change_mode

@repeat_question
def play_question_again():
    return

@repeat_question
def toggle_alt_chord_tone_res():
    st.ALTERNATIVE_CHORD_TONE_RESOLUTION = (st.ALTERNATIVE_CHORD_TONE_RESOLUTION + 1) % 3
    print("Switching to chord tone resolution "
          "option {}".format(st.ALTERNATIVE_CHORD_TONE_RESOLUTION))

    

menu_commands = [
    gs.MenuCommand("v", "hear the cadence", play_cadence),
    gs.MenuCommand("w", "change the delay between chords", set_delay),
    gs.MenuCommand("s", "toggle between hearing triads and hearing seventh chords", toggle_triads7ths),
    gs.MenuCommand("k", "change the key", set_key),
    gs.MenuCommand("o", "toggle between using one octave or many", toggle_many_octaves),
    gs.MenuCommand("m", "to arpeggiate chord (not available in progression mode)", arpeggiate),
    gs.MenuCommand("p", "switch to random progression mode (experimental)", change_game_mode('progression')),
    gs.MenuCommand("t", "switch to chord tone mode", change_game_mode('chord_tone')),
    gs.MenuCommand("h", "switch to single chord mode", change_game_mode('single_chord')),
    gs.MenuCommand("i", "toggle between chord tone resolutions", toggle_alt_chord_tone_res),
    gs.MenuCommand("x", "quit", sys.exit),
    gs.MenuCommand("", "hear the chord or progression again", play_question_again,
                 input_description="Press Enter"),
]
menu_commands = dict([(mc.command, mc) for mc in menu_commands])


# Game Mode Intro Functions
def intro(play_cadence=True):
    print("\n" + "~" * 20 + "\n")

    # List menu_commands
    print("Note: At any time enter")
    for mc in menu_commands.values():
        print(mc.input_description, "to", mc.description)
    print("\n" + "-" * 10 + "\n")

    # Display key
    if st.KEY == st.KEY.lower():
        print("KEY:", st.KEY.upper(), "min")
    else:
        print("KEY:", st.KEY, "Maj")
    print("-" * 10)

    # Play cadence
    if play_cadence:
        play_progression(st.CADENCE, st.KEY, delay=st.DELAY, Iup=st.I)
        time.sleep(st.DELAY)
    time.sleep(st.DELAY)
    return


def intro_single_chord():
    intro()


def intro_progression():
    intro()


def intro_chord_tone():
    intro(False)


# New Question Functions
@new_question
def eval_single_chord(usr_ans, correct_numeral, root_note):
    correct_ = False
    if usr_ans == str(st.NUMERALS.index(correct_numeral) + 1):
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


def new_question_single_chord():
    # Choose new chord+octave/Progression
    # Single chord mode
    if st.NEWQUESTION:
        if st.COUNT:
            print("score: {} / {} = {:.2%}".format(st.SCORE, st.COUNT, st.SCORE/st.COUNT))
        st.COUNT += 1

        # Pick random chord/octave
        numeral, chord, Ioctave = random_chord()

        # store question info
        st.CURRENT_Q_INFO = {'numeral': numeral,
                             'chord': chord,
                             'Ioctave': Ioctave}
    else:
        numeral = st.CURRENT_Q_INFO['numeral']
        chord = st.CURRENT_Q_INFO['chord']
        Ioctave = st.CURRENT_Q_INFO['Ioctave']

    # Play chord
    play_progression([numeral], st.KEY, Ioctave=Ioctave)

    # Request user's answer
    ans = getch("Enter 1-7 or root of chord: ").strip()

    if ans in menu_commands:
        menu_commands[ans].action()
    else:
        if isvalidnote(ans):
            if eval_single_chord(ans, numeral, chord[0].name):
                st.SCORE += 1
                print("Yes!", chordname(chord, numeral))
                if st.RESOLVE_WHEN_CORRECT:
                    resolve_with_chords(numeral, key=st.KEY, Ioctave=Ioctave, 
                        numerals=st.NUMERALS, delay=st.DELAY / 2)
                    time.sleep(st.DELAY)
            else:
                print("No!", chordname(chord, numeral))
                if st.RESOLVE_WHEN_INCORRECT:
                    resolve_with_chords(numeral, key=st.KEY, Ioctave=Ioctave, 
                        numerals=st.NUMERALS, delay=st.DELAY / 2)
                    time.sleep(st.DELAY)
        else:
            print("User input not understood.  Please try again.")
    return


@new_question
def eval_progression(ans, prog, prog_strums):
    try:
        int(ans)
        answers = [x for x in ans]
    except:
        answers = ans.split(" ")

    answers_correct = []
    for i, answer in enumerate(answers):
        try:
            correct_numeral = prog[i]
            root = NoteContainer(progressions.to_chords([correct_numeral], st.KEY)[0])[0].name
            user_correct = eval_single_chord(answer, correct_numeral, root)
            print(user_correct)
            answers_correct.append(user_correct)
        except IndexError:
            print("too many answers")
    if len(answers) < len(prog):
        print("too few answers")

    print("Progression:", " ".join(prog_strums))
    print("Correct Answer:", " ".join([str(st.NUMERALS.index(x) + 1) for x in prog]))

    if all(answers_correct):
        st.SCORE += 1
        print("Good Job!")
        print()
    else:
        print("It's ok, you'll get 'em next time.")
        print()
    time.sleep(st.DELAY)


def new_question_progression():
    if st.NEWQUESTION:
        if st.COUNT:
            print("score: {} / {} = {:.2%}".format(st.SCORE, st.COUNT, st.SCORE/st.COUNT))
        st.COUNT += 1
        # Find random chord progression
        prog_length = random.choice(st.PROG_LENGTHS)
        prog, prog_strums = random_progression(prog_length, st.NUMERALS, st.CHORD_LENGTHS)

        # store question info
        st.CURRENT_Q_INFO = {'prog': prog,
                             'prog_strums': prog_strums}
    else:
        prog = st.CURRENT_Q_INFO['prog']
        prog_strums = st.CURRENT_Q_INFO['prog_strums']

    # Play chord/progression
    play_progression(prog_strums, st.KEY, delay=st.DELAY)

    # Request user's answer
    ans = input("Enter your answer using root note names "
                "or numbers 1-7 seperated by spaces: ").strip()

    if ans in menu_commands:
        menu_commands[ans].action()
    else:
        eval_progression(ans, prog, prog_strums)

    # # Request user's answer
    # ans = input("Enter your answer using root note names "
    #             "or numbers 1-7 seperated by spaces: ").strip()
    # if ans in menu_commands:
    #     menu_commands[ans].action()
    # else:
    #     eval_progression(ans, prog, prog_strums)


# @new_question
# def eval_chord_tone(ans, chord, tone):
#     tone_idx = [n for n in chord].index(tone)
#     correct_ans = st.TONES[tone_idx]
#     return ans == correct_ans


def resolve_chord_tone(chord, tone, Ioctave):
    # play_progression([numeral], st.KEY, Ioctave=Ioctave)

    if st.ALTERNATIVE_CHORD_TONE_RESOLUTION == 1:
        fluidsynth.play_NoteContainer(chord)
        time.sleep(st.DELAY)
        fluidsynth.play_Note(tone)
        time.sleep(st.DELAY)
        root = chord[0]
        interval = NoteContainer([root, tone])
        fluidsynth.play_NoteContainer(interval)
    elif st.ALTERNATIVE_CHORD_TONE_RESOLUTION == 2:
        fluidsynth.play_NoteContainer(chord)
        time.sleep(st.DELAY)
        tone_idx = [x for x in chord].index(tone)
        if tone_idx == 0:
            arpeggiate()
        elif tone_idx == 1:
            arpeggiate(invert=[1, 0, 2])
        elif tone_idx == 2:
            arpeggiate(descending=True)
        else:
            raise Exception("This chord tone resolutions mode is only implemented for triads.")

        # fluidsynth.play_Note(Iup_note)
        # Iup_note = Note(st.KEY)
        # Iup_note.octave += 1
        # fluidsynth.play_Note(Iup_note)
    else:
        fluidsynth.play_NoteContainer(chord)
        time.sleep(st.DELAY)
        fluidsynth.play_Note(tone)
        time.sleep(st.DELAY)
        arpeggiate()  # sets NEWQUESTION = False
    

def new_question_chord_tone():
    if st.NEWQUESTION:
        if st.COUNT:
            print("score: {} / {} = {:.2%}".format(st.SCORE, st.COUNT, st.SCORE/st.COUNT))
        st.COUNT += 1

        # Pick random chord/octave
        numeral, chord, Ioctave = random_chord()

        # Pick a random tone in the chord
        tone = random.choice(chord)

        # store question info
        st.CURRENT_Q_INFO = {'numeral': numeral,
                             'chord': chord,
                             'Ioctave': Ioctave,
                             'tone': tone}
    else:
        numeral = st.CURRENT_Q_INFO['numeral']
        chord = st.CURRENT_Q_INFO['chord']
        Ioctave = st.CURRENT_Q_INFO['Ioctave']
        tone = st.CURRENT_Q_INFO['tone']

    # Play chord, then tone
    def playfcn():
        play_progression([numeral], st.KEY, Ioctave=Ioctave)
        time.sleep(st.DELAY)
        fluidsynth.play_Note(tone)
    p = Process(target=playfcn())
    p.start()

    # Request user's answer
    mes = ("Which tone did you hear?\n""Enter {}, or {}: ".format(
            ", ".join([str(t) for t in st.TONES[:-1]]),
            st.TONES[-1]))
    ans = getch(mes).strip()
    p.terminate()

    if ans in menu_commands:
        menu_commands[ans].action()
    else:
        try:
            ans = int(ans)
        except:
            print("User input not understood.  Please try again.")
            st.NEWQUESTION = False

        if ans in st.TONES:
            tone_idx = [n for n in chord].index(tone)
            correct_ans = st.TONES[tone_idx]
            if ans == correct_ans:
                st.SCORE += 1
                print("Yes! The {} tone of".format(correct_ans), chordname(chord, numeral))
                if st.ARPEGGIATE_WHEN_CORRECT:
                    resolve_chord_tone(chord, tone, Ioctave)
                    time.sleep(st.DELAY)
                    st.NEWQUESTION = True
            else:
                print("No! The {} tone of".format(correct_ans), chordname(chord, numeral))
                if st.ARPEGGIATE_WHEN_INCORRECT:
                    resolve_chord_tone(chord, tone, Ioctave)
                    time.sleep(st.DELAY)
                    st.NEWQUESTION = True

        # secret option
        elif ans in [8, 9, 0]:
            tone_idx = [8, 9, 0].index(ans)
            for num in st.NUMERALS:
                num_chord = NoteContainer(progressions.to_chords([num], st.KEY)[0])
                play_progression([num], st.KEY, Ioctave=Ioctave)
                time.sleep(st.DELAY)
                fluidsynth.play_Note(num_chord[tone_idx])
                time.sleep(st.DELAY)
            time.sleep(st.DELAY)
            st.NEWQUESTION = False

        else:
            print("User input not understood.  Please try again.")
            st.NEWQUESTION = False
    return


game_modes = {
    'single_chord': gs.GameMode(intro_single_chord, new_question_single_chord),
    'progression': gs.GameMode(intro_progression, new_question_progression),
    'chord_tone': gs.GameMode(intro_chord_tone, new_question_chord_tone),
    }