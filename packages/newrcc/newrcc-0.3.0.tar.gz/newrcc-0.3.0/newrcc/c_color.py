from typing import Union, Tuple

from newrcc import c_error

__all__ = [
    'RESET',
    'TextColor',
    'BackgroundColor',
    'Decoration'
]

RESET = '\033[0m'


class Color:
    def __init__(self, color: Union[str, Tuple[int, int, int]]):
        if isinstance(color, str):
            self.colorcode = color
        elif isinstance(color, tuple):
            Color.__RGBColor(self, color)
        else:
            raise CError.CDColorUndefinedError(color)

    def __RGBColor(self, color: Tuple[int, int, int]):
        for code in color:
            if not (0 <= code <= 255):
                raise CError.CDColorUndefinedError(color)
        if isinstance(self, TextColor):
            _type = '38'
        elif isinstance(self, BackgroundColor):
            _type = '48'
        else:
            raise CError.CDColorUndefinedError(color)
        self.colorcode = f'\033[{_type};2;{color[0]};{color[1]};{color[2]}m'

    def __str__(self):
        return self.colorcode


class TextColor(Color):
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    GRAY = '\033[90m'
    WHITE = '\033[38m'
    LIGHT_GRAY = '\033[37m'
    LIGHT_RED = '\033[91m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_YELLOW = '\033[93m'
    LIGHT_BLUE = '\033[94m'
    LIGHT_PURPLE = '\033[95m'
    LIGHT_CYAN = '\033[96m'
    LIGHT_WHITE = '\033[97m'

    def __init__(self, color: Union[str, Tuple[int, int, int]]):
        super().__init__(color)


class BackgroundColor(Color):
    BLACK = '\033[40m'
    RED = '\033[41m'
    GREEN = '\033[42m'
    YELLOW = '\033[43m'
    BLUE = '\033[44m'
    PURPLE = '\033[45m'
    CYAN = '\033[46m'
    GRAY = '\033[47m'

    def __init__(self, color: Union[str, Tuple[int, int, int]]):
        super().__init__(color)


class Decoration:
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    L_UNDERLINE = '\033[4m'
    REVERSE = '\033[7m'
    LINE_THROUGH = '\033[9m'
    B_UNDERLINE = '\033[21m'

    def __init__(self, decoration: str):
        self.decoration = decoration

    def __str__(self):
        return self.decoration


def main():
    print(f"{TextColor.WHITE}你好{TextColor.LIGHT_GRAY}hello{TextColor.GRAY}world{RESET}")


if __name__ == '__main__':
    main()
