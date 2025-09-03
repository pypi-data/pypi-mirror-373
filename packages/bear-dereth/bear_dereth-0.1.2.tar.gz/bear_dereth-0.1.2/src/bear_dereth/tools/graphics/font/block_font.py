"""A dictionary containing ASCII art representations of letters and symbols in a block font style."""

from rich.align import Align
from rich.console import Console

from bear_dereth.tools.graphics.font import FontStyle

from ._raw_block_letters import (
    ASTERISK,
    AT,
    BACKWARD_SLASH,
    COMMA,
    DASH,
    DOLLAR,
    DOT,
    EIGHT,
    EQUALS,
    EXCLAMATION,
    FIVE,
    FORWARD_SLASH,
    FOUR,
    HASH,
    NINE,
    ONE,
    PLUS,
    QUESTION,
    SEVEN,
    SIX,
    SPACE,
    THREE,
    TWO,
    UNDERSCORE,
    ZERO,
    A,
    B,
    C,
    D,
    E,
    F,
    G,
    H,
    I,
    J,
    K,
    L,
    M,
    N,
    O,
    P,
    Q,
    R,
    S,
    T,
    U,
    V,
    W,
    X,
    Y,
    Z,
)
from ._theme import CyberTheme as Theme
from ._utils import random_style

BLOCK_LETTERS: dict[str, list[str]] = {
    "A": A,
    "B": B,
    "C": C,
    "D": D,
    "E": E,
    "F": F,
    "G": G,
    "H": H,
    "I": I,
    "J": J,
    "K": K,
    "L": L,
    "M": M,
    "N": N,
    "O": O,
    "P": P,
    "Q": Q,
    "R": R,
    "S": S,
    "T": T,
    "U": U,
    "V": V,
    "W": W,
    "X": X,
    "Y": Y,
    "Z": Z,
    "0": ZERO,
    "1": ONE,
    "2": TWO,
    "3": THREE,
    "4": FOUR,
    "5": FIVE,
    "6": SIX,
    "7": SEVEN,
    "8": EIGHT,
    "9": NINE,
    " ": SPACE,
    "!": EXCLAMATION,
    "?": QUESTION,
    ".": DOT,
    ",": COMMA,
    "-": DASH,
    "_": UNDERSCORE,
    "=": EQUALS,
    "+": PLUS,
    "*": ASTERISK,
    "/": FORWARD_SLASH,
    "\\": BACKWARD_SLASH,
    "@": AT,
    "#": HASH,
    "$": DOLLAR,
}

console = Console()


def apply_block_style(block_rows: list[str], style: str = "solid") -> list[str]:
    """Replace block characters with different symbols."""
    try:
        new_char: FontStyle = FontStyle.get(value=style, default=FontStyle.SOLID)
        return [row.replace(FontStyle.SOLID.text, new_char.text) for row in block_rows]
    except (KeyError, AttributeError) as e:
        available = ", ".join(FontStyle.keys())
        raise ValueError(f"Invalid style: {style}. Available styles: {available}") from e


def char_to_block(char: str) -> list[str]:
    """Convert a single character to its block font representation."""
    return BLOCK_LETTERS.get(char.upper(), ["        "] * 5)


def _word_to_block(word: str) -> list[str]:
    """Convert a word to its block font representation."""
    clean_text: str = "".join(char for char in word.upper() if char in BLOCK_LETTERS)

    if not clean_text:
        return ["No valid characters to block-ify! 🧱"]

    rows = ["", "", "", "", ""]
    for char in clean_text:
        block_char = char_to_block(char)
        for i in range(5):
            rows[i] += block_char[i]
    return rows


def word_to_block(word: str, font: str = "solid") -> str:
    """Convert a word to its block font representation as a single string.

    Args:
        word (str): The word to convert.
        font (str): The style of the block font. Defaults to "solid".

    Returns:
        str: The block font representation of the word.
    """
    block_rows = _word_to_block(word)
    styled_rows = apply_block_style(block_rows, font)
    return "\n".join(styled_rows)


def print_block_font(text: str, color: str = Theme.neon_green) -> None:
    """Print block font text with cyberpunk styling."""
    block_rows = _word_to_block(text)

    for row in block_rows:
        console.print(Align.center(f"[{color}]{row}[/{color}]"))


def show_off_styles(word: str, style: str | None = None) -> None:
    """Display all block styles by using an example word"""
    console.print("Available block styles:")

    for symbol in FontStyle:
        styled_word = word_to_block(word, font=symbol)
        style = random_style()

        console.print()
        console.print(Align.center(f"[{Theme.system}]{symbol.title()} Style:[/]"))
        console.print(Align.center(f"[{style}]{styled_word}[/]"))
        console.print()


__all__ = ["BLOCK_LETTERS", "char_to_block", "word_to_block"]
# fmt: on

if __name__ == "__main__":
    WORD = "BEAR"
    show_off_styles(WORD)
