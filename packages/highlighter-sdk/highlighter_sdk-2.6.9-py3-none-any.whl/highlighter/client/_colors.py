from functools import partial

from colorama import Back, Fore, Style


def message_in_color(color: str, message: str):
    return color + message + Fore.RESET


red = partial(message_in_color, Fore.RED)
green = partial(message_in_color, Fore.GREEN)


def message_in_color_front_and_back(front_color: str, back_color: str, style: str, message: str):
    message = front_color + message + Fore.RESET
    if back_color is None:
        return message

    message = back_color + message + Back.RESET
    if style is None:
        return message

    return style + message + Style.RESET_ALL


class ColoredString:
    FRONT_COLORS = [x.lower() for x in vars(Fore) if x != "RESET"]
    BACK_COLORS = [x.lower() for x in vars(Back) if x != "RESET"]
    STYLES = [x.lower() for x in vars(Style) if x != "RESET_ALL"]
    """
    cs = ColoredString()
    print(cs.red("abd"))
    print(cs.red_black("abc"))
    print(cs.red_black_bright("abc"))
    """

    def __init__(self):
        self.cache = {}

    def __getattr__(self, name):
        if name in self.cache:
            return self.cache[name]

        colors = name.split("_")
        back_color = None
        style = None

        if len(colors) == 1:
            front_color = colors[0]
        elif len(colors) == 2:
            front_color, back_color = colors
        else:
            front_color, back_color, style = colors[:3]

        front_colors = ColoredString.FRONT_COLORS
        if front_color not in front_colors:
            raise ValueError("available front colors:", front_colors)

        back_colors = ColoredString.BACK_COLORS
        if back_color and back_color not in back_colors:
            raise ValueError("available back colors:", back_colors)

        styles = ColoredString.STYLES
        if style and style not in styles:
            raise ValueError("available style:", styles)

        func = partial(
            message_in_color_front_and_back,
            getattr(Fore, front_color.upper()),
            getattr(Back, back_color.upper()) if back_color else None,
            getattr(Style, style.upper()) if style else None,
        )

        self.cache[name] = func
        return func


if __name__ == "__main__":
    cs = ColoredString()
    print(cs.red_black_bright("abc"))
    # print(cs.black_red("abc"))
    # print(cs.black_red_dim("abc"))
    # print(cs.funcs)
    # print(cs.red_yellow("abc"))
    # print(cs.red_black("cba"))
    # print(cs.black_green("abc"))
