
class COLORS:
    def __init__(self):
        ...

    # region Cores
    # ----------------------------------------------
    @property
    def __colors__(self):
        result = {"black": {"fore": "\033[1;30m", "back": "\033[1;40m"},
                  "red": {"fore": "\033[1;31m", "back": "\033[1;41m"},
                  "green": {"fore": "\033[1;32m", "back": "\033[1;42m"},
                  "yellow": {"fore": "\033[1;33m", "back": "\033[1;43}"},
                  "blue": {"fore": "\033[1;34m", "back": "\033[1;44m"},
                  "magenta": {"fore": "\033[1;35m", "back": "\033[1;4}m"},
                  "cyan": {"fore": "\033[1;36m", "back": "\033[1;46m"},
                  "gray light": {"fore": "\033[1;37m", "back": "\033}1;47m"},
                  "gray dark": {"fore": "\033[1;90m", "back": "\033[1;100m}"},
                  "red light": {"fore": "\033[1;91m", "back": "\033[1;101}"},
                  "green light": {"fore": "\033[1;92m", "back": "\033[1;102m"},
                  "yellow light": {"fore": "\033[1;93m", "back": "\033[1;103}"},
                  "blue light": {"fore": "\033[1;94m", "back": "\033[1;104m"},
                  "magenta light": {"fore": "\033[1;95m", "back": "\033[1;10}m"},
                  "cyan light": {"fore": "\033[1;96m", "back": "\033[1;106m"},
                  "white": {"fore": "\033[1;97m", "back": "\033[1;107m"},
                  "bold": {"fore": "\033[;1m", "back": None},
                  "italic": {"fore": "\033[;3m", "back": None},
                  "underline": {"fore": "\033[;4m", "back": None},
                  "crossedout": {"fore": "\033[;9m", "back": None},
                  "inverse": {"fore": "\033[;7m", "back": None},
                  "reverse": {"fore": "\033[;17m", "back": None},
                  "reset": {"fore": "\033[0;0m", "back": None},
                  }
        return result

    @property
    def black_fore(self):
        return self.__colors__["black"]["fore"]

    @property
    def black_back(self):
        return self.__colors__["black"]["back"]

    @property
    def red_fore(self):
        return self.__colors__["red"]["fore"]

    @property
    def red_back(self):
        return self.__colors__["red"]["back"]

    @property
    def green_fore(self):
        return self.__colors__["green"]["fore"]

    @property
    def green_back(self):
        return self.__colors__["green"]["back"]

    @property
    def green_light_fore(self):
        return self.__colors__["green light"]["fore"]

    @property
    def green_light_back(self):
        return self.__colors__["green light"]["back"]

    @property
    def yellow_fore(self):
        return self.__colors__["yellow"]["fore"]

    @property
    def yellow_back(self):
        return self.__colors__["yellow"]["back"]

    @property
    def blue_fore(self):
        return self.__colors__["blue"]["fore"]

    @property
    def blue_back(self):
        return self.__colors__["blue"]["back"]

    @property
    def magenta_fore(self):
        return self.__colors__["magenta"]["fore"]

    @property
    def magenta_back(self):
        return self.__colors__["magenta"]["back"]

    @property
    def cyan_fore(self):
        return self.__colors__["cyan"]["fore"]

    @property
    def cyan_back(self):
        return self.__colors__["cyan"]["back"]

    @property
    def gray_light_fore(self):
        return self.__colors__["gray light"]["fore"]

    @property
    def gray_light_back(self):
        return self.__colors__["gray light"]["back"]

    @property
    def gray_dark_fore(self):
        return self.__colors__["gray dark"]["fore"]

    @property
    def gray_dark_back(self):
        return self.__colors__["gray dark"]["back"]

    @property
    def red_light_fore(self):
        return self.__colors__["red light"]["fore"]

    @property
    def red_light_back(self):
        return self.__colors__["red light"]["back"]

    @property
    def green_light_fore(self):
        return self.__colors__["green light"]["fore"]

    @property
    def green_light_back(self):
        return self.__colors__["green light"]["back"]

    @property
    def yellow_light_fore(self):
        return self.__colors__["yellow light"]["fore"]

    @property
    def yellow_light_back(self):
        return self.__colors__["yellow light"]["back"]

    @property
    def blue_light_fore(self):
        return self.__colors__["blue light"]["fore"]

    @property
    def blue_light_back(self):
        return self.__colors__["blue light"]["back"]

    @property
    def magenta_light_fore(self):
        return self.__colors__["magenta light"]["fore"]

    @property
    def magenta_light_back(self):
        return self.__colors__["magenta light"]["back"]

    @property
    def cyan_light_fore(self):
        return self.__colors__["cyan light"]["fore"]

    @property
    def cyan_light_back(self):
        return self.__colors__["cyan light"]["back"]

    @property
    def white_fore(self):
        return self.__colors__["white"]["fore"]

    @property
    def white_back(self):
        return self.__colors__["white"]["back"]

    # endregion

    # region Efeitos
    @property
    def bold(self):
        return self.__colors__["bold"]["fore"]

    @property
    def italic(self):
        return self.__colors__["italic"]["fore"]

    @property
    def underline(self):
        return self.__colors__["underline"]["fore"]

    @property
    def crossedout(self): # riscado
        return self.__colors__["crossedout"]["fore"]

    @property
    def inverse(self):
        return self.__colors__["inverse"]["fore"]

    @property
    def reverse(self):
        return self.__colors__["reverse"]["fore"]

    @property
    def reset(self):
        return self.__colors__["reset"]["fore"]

    # endregion