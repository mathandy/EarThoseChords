""""
This module sets of the getch() function, which is like input(), but only
takes a single character, and doesn't require the user to press enter.
Credit:
https://stackoverflow.com/questions/510357/python-read-a-single-character-from-the-user
"""


# For python 3 compatibility
from __future__ import division, absolute_import, print_function
try: input = raw_input
except: pass


class _Getch:
    """Gets a single character from standard input.  Does not echo to the
    screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


def getch(message=None):
    if message:
        print(message)
    getchfunc = _Getch()
    return getchfunc()