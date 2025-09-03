"""Ascii art glitch font generator for cyberpunk vibes!"""

from io import StringIO
import random

GLITCH_CHARS: list[str] = ["█", "▓", "░", "▒", "■", "□", "▪", "▫"]


def dice_roll(chance: float) -> bool:
    """Roll a dice with a given chance."""
    return random.random() < chance  # noqa: S311, we aren't doing crypto bro


def dice_roll_choice(choices: list[str], chance: float = 0.5) -> str:
    """Roll a dice to choose from a list of choices with a given chance."""
    if dice_roll(chance):
        return random.choice(choices)  # noqa: S311, we aren't doing crypto bro
    return ""


def glitch_font_generator(text: str, glitch_intensity: float = 0.3) -> str:
    """Generate beautifully corrupted glitch text with MIXED characters."""
    output = StringIO()

    for char in text.upper():
        if char == " ":
            output.write(" ")
            continue

        output.write(char)
        symbol: str = dice_roll_choice(GLITCH_CHARS, glitch_intensity)
        output.write(symbol)
        symbol2: str = dice_roll_choice(GLITCH_CHARS, glitch_intensity * 0.4)
        output.write(symbol2)

    result: str = output.getvalue()
    output.close()
    return result


def multi_line_glitch(*lines: str, base_intensity: float = 0.3) -> str:
    """Generate glitch effects for multiple lines with StringIO magic."""
    output = StringIO()

    for i, line in enumerate(lines):
        intensity: float = base_intensity + (i * 0.1)
        glitched_line: str = glitch_font_generator(line, intensity)
        output.write(glitched_line)

        if i < len(lines) - 1:
            output.write("\n")

    result = output.getvalue()
    output.close()
    return result


def cyberpunk_glitch_font(*text: str, style: str = "heavy") -> str:
    """Different glitch styles for maximum chaos."""
    styles = {"light": 0.2, "medium": 0.4, "heavy": 0.6, "corrupted": 0.8}

    intensity: float = styles.get(style, 0.4)
    return multi_line_glitch(*text, base_intensity=intensity)
