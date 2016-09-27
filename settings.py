# For python 3 compatibility
from __future__ import division, absolute_import, print_function
try: input = raw_input
except: pass

# External Dependencies
import argparse, os
import mingus.core.notes as notes


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


# Setup settings for use in other modules
user_args = get_user_args()
SOUNDFONT = user_args.sound_font

if user_args.minor:
    KEY = user_args.key.lower()
else:
    KEY = user_args.key.upper()

if user_args.sevenths:
    [I, II, III, IV, V, VI, VII] = ["I7", "II7", "III7", "IV7", "V7", "VI7", "VII7"]
    TONES = [1, 3, 5, 7]
else:
    [I, II, III, IV, V, VI, VII] = ["I", "II", "III", "IV", "V", "VI", "VII"]
    TONES = [1, 3, 5]

CADENCE = [I, IV, V, I]
NUMERALS = [I, II, III, IV, V, VI, VII]

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
ARPEGGIATE_WHEN_CORRECT = True
ARPEGGIATE_WHEN_INCORRECT = True

OCTAVES = range(1, 8)  # if many_octaves flag invoked
DEFAULT_IOCTAVE = 4
INITIAL_MODE = 'chord_tone'

# Inelegant storage
NEWQUESTION = True
CURRENT_MODE = None
CURRENT_Q_INFO = None
SCORE = 0
COUNT = 0
ALTERNATIVE_CHORD_TONE_RESOLUTION = 2