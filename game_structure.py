# For python 3 compatibility
from __future__ import division, absolute_import, print_function
try: input = raw_input
except: pass


class MenuCommand:
    def __init__(self, command, description, action_fcn, input_description=None):
        self.command = command
        self.description = description
        self.action_fcn = action_fcn
        if not input_description:
            self.input_description = command
        else:
            self.input_description = input_description

    def action(self, *args, **kwargs):
        self.action_fcn(*args, **kwargs)


class SettingsContainer(object):
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])


class GameMode:
    def __init__(self, name, intro_fcn, new_question_fcn, menu_fcn=None, mode_specific_settings=None):
        self.name = name
        self.intro_fcn = intro_fcn
        self.new_question_fcn = new_question_fcn
        self.menu_fcn = menu_fcn
        self.settings = mode_specific_settings

    def intro(self, *args, **kwargs):
        self.intro_fcn(*args, **kwargs)

    def new_question(self, *args, **kwargs):
        self.new_question_fcn(*args, **kwargs)

    def eval(self, *args, **kwargs):
        self.eval_fcn(*args, **kwargs)

    def menu(self, *args, **kwargs):
        self.menu_fcn(*args, **kwargs)


class Game:
    def __init__(self, play_game_fcn, game_modes, initial_mode, glob_settings=None):
        self.play_game_fcn = play_game_fcn
        self.game_modes = game_modes
        self.current_mode = initial_mode
        self.settings = glob_settings

    def play(self, *args, **kwargs):
        self.play_game_fcn(*args, **kwargs)