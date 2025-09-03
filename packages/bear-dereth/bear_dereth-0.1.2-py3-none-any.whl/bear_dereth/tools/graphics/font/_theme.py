from bear_dereth.tools.rich_enums import RichStrEnum, StrValue


class CyberTheme(RichStrEnum):
    """Namespace for cyberpunk color theme constants."""

    primary = StrValue("bright_magenta", "Primary color")
    neon_green = StrValue("bright_green", "Neon green color")
    neon_cyan = StrValue("bright_cyan", "Neon cyan color")
    warning = StrValue("bright_yellow", "Warning color")
    error = StrValue("bright_red", "Error color")
    credits = StrValue("bright_yellow", "Credits color")
    data = StrValue("bright_blue", "Data color")
    system = StrValue("dim white", "System color")


class FontStyle(RichStrEnum):
    """Enumeration for block font styles."""

    SOLID = StrValue("solid", "█")
    HOLLOW = StrValue("hollow", "░")
    PIPES = StrValue("pipes", "|")
    OUTLINE = StrValue("outline", "■")
    DASHED = StrValue("dashed", "─")
    DOTTED = StrValue("dotted", "·")
    ZIGZAG = StrValue("zigzag", "╱")  # noqa: RUF001
    CROSSED = StrValue("crossed", "╳")  # noqa: RUF001
    FANCY = StrValue("fancy", "◆")
    RIGHT_ARROWS = StrValue("right_arrows", "▶")
    LEFT_ARROWS = StrValue("left_arrows", "◀")
    STARS = StrValue("stars", "★")
