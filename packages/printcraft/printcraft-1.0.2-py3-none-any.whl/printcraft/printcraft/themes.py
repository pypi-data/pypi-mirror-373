# printcraft/themes.py

"""
Themes and styling utilities for PrintCraft.
Centralized color handling for consistent output across formatters.
"""

from colorama import Fore, Style, init

# Initialize colorama once
init(autoreset=True)

# Theme definitions
THEMES = {
    "default": {"color": Fore.WHITE},
    "red": {"color": Fore.RED},
    "green": {"color": Fore.GREEN},
    "yellow": {"color": Fore.YELLOW},
    "blue": {"color": Fore.BLUE},
    "magenta": {"color": Fore.MAGENTA},
    "cyan": {"color": Fore.CYAN},
    "bold": {"color": Style.BRIGHT},
    "dim": {"color": Style.DIM},
    "reset": {"color": Style.RESET_ALL},
}

def get_theme(name: str):
    """Return color dict for the given theme"""
    return THEMES.get(name, THEMES["default"])



def apply_theme(text: str, theme: str = "default", enable: bool = True) -> str:
    """
    Apply a color theme to text.

    Args:
        text: The text to style.
        theme: Name of the theme (see THEMES).
        enable: If False, return text without styling.
    """
    if not enable:
        return text

    style = THEMES.get(theme, THEMES["default"])["color"]
    reset = Style.RESET_ALL
    return f"{style}{text}{reset}"
