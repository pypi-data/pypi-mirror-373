from ..constants.colors import all_colors, RESET

def u_color(text: str, color: str = "red", i: int = 0, r: int = 0, g: int = 0, b: int = 0) -> str:
    if color.lower() in ["256", "256f", "foreground_256"]:
        color_code = "\033[38;5;{i}m".format(i=i)
    elif color.lower() in ["256b", "background_256"]:
        color_code = "\033[48;5;{i}m".format(i=i)
    elif color.lower() in ["rgb", "rgbf", "foreground_rgb"]:
        color_code = "\033[38;2;{r};{g};{b}m".format(r=r, g=g, b=b)
    elif color.lower() in ["rgbb", "background_rgb"]:
        color_code = "\033[48;2;{r};{g};{b}m".format(r=r, g=g, b=b)
    else:
        color_code = all_colors.get(color.lower(), RESET)
    return f"{color_code}{text}{RESET}"


def highlight_args(text):
    words = text.split()
    result = []
    prev_is_arg = False
    for word in words:
        if word.startswith("-"):
            result.append(u_color(word, "green"))
            prev_is_arg = True
        elif prev_is_arg:
            result.append(u_color(word, "red"))
            prev_is_arg = False
        else:
            result.append(word)
    return " ".join(result)