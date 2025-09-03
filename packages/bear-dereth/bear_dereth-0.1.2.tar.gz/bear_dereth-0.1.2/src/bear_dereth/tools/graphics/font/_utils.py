from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
import os
from typing import cast

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from bear_dereth.tools.graphics.bear_gradient import ColorGradient
from bear_dereth.tools.graphics.font import FontStyle
from bear_dereth.tools.rich_enums import RichStrEnum, StrValue as Value

HAS_PYFIGLET = False
try:
    from pyfiglet import figlet_format  # type: ignore[import]

    HAS_PYFIGLET = True
except ImportError:
    ...


def random_num(rng: int = 100) -> int:
    """Generate a random number between 0 and the specified range."""
    random_bytes: bytes = os.urandom(1)
    random_index: int = int.from_bytes(random_bytes, "big") % rng
    return random_index


def random_style() -> str:
    rnd_index: int = random_num(100)
    gradient = ColorGradient()
    return gradient.map_to_rgb(0, 100, rnd_index)


class FigletFonts(RichStrEnum):
    """Namespace for Figlet font constants."""

    COMPUTER = Value("computer", "Computer font")
    SLANT = Value("slant", "Slant font")
    STANDARD = Value("standard", "Standard font")
    SMALL = Value("small", "Small font")
    BIG = Value("big", "Big font")
    BLOCK = Value("block", "Block font")
    STAR_WARS = Value("starwars", "Star Wars font")
    CYBER_MEDIUM = Value("cybermedium", "Cyber Medium font")
    CYBER_LARGE = Value("cyberlarge", "Cyber Large font")
    CYBER_SMALL = Value("cybersmall", "Cyber Small font")
    ANSI_SHADOW = Value("ansi_shadow", "ANSI Shadow font")
    BLOODY = Value("bloody", "Bloody font")
    BANNER_3_D = Value("banner3-D", "Banner 3-D font")
    POISON = Value("poison", "Poison font")
    ALPHA = Value("alpha", "Alpha font")
    DOOM = Value("doom", "Doom font")
    DOT_MATRIX = Value("dotmatrix", "Dot Matrix font")
    JAZMINE = Value("jazmine", "Jazmine font")
    RAMMSTEIN = Value("rammstein", "Rammstein font")
    GHOST = Value("ghost", "Ghost font")
    DIAGONAL_3D = Value("3d_diagonal", "Diagonal 3D font")


@dataclass
class HeaderConfig:
    """Configuration for header styling."""

    top_sep: str = "#"
    left_sep: str = ">"
    right_sep: str = "<"
    bottom_sep: str = "#"
    length: int = 60
    title_style: str = "bold red"  # s1
    border_style: str = "bold blue"  # s2 - top/bottom lines
    separator_style: str = "bold green"  # s3 - left/right separators
    overall_style: str = "bold yellow"  # s4
    border_enabled: bool = True
    center_align: bool = True
    return_txt: bool = False
    use_panel: bool = False


class TextHelper:
    def _create_separator_line(self, char: str, length: int, style: str) -> Text:
        """Create a styled separator line."""
        return Text(char * length, style=style)

    def _create_title_line_manual(self, title: str, cfg: HeaderConfig) -> Text:
        """Create title line with manual separator padding."""
        title_with_spaces = f" {title} "
        title_length = len(title_with_spaces)
        remaining_space = cfg.length - title_length
        left_padding = remaining_space // 2
        right_padding = remaining_space - left_padding
        title_line = Text()
        title_line.append(cfg.left_sep * left_padding, style=cfg.separator_style)
        title_line.append(f" {title} ", style=cfg.title_style)
        title_line.append(cfg.right_sep * right_padding, style=cfg.separator_style)
        return title_line

    def _create_title_line_rich(self, title: str, cfg: HeaderConfig) -> Text:
        """Create title line using Rich's alignment."""
        styled_title = Text(f" {title} ", style=cfg.title_style)
        title_line = Text()
        title_line.append(cfg.left_sep, style=cfg.separator_style)
        title_line.append(styled_title)
        title_line.append(cfg.right_sep, style=cfg.separator_style)
        return Text.from_markup(str(Align.center(title_line, width=cfg.length)))

    def _create_panel_header(self, title: str, cfg: HeaderConfig) -> Panel:
        """Create header using Rich Panel."""
        return Panel(
            f"[{cfg.title_style}]{title}[/{cfg.title_style}]",
            width=cfg.length,
            border_style=cfg.border_style,
            expand=False,
        )

    def _create_manual_header(self, title: str, cfg: HeaderConfig) -> list[Text]:
        """Create header using manual separator lines."""
        top_line = self._create_separator_line(cfg.top_sep, cfg.length, cfg.border_style)
        bottom_line = self._create_separator_line(cfg.bottom_sep, cfg.length, cfg.border_style)
        title_line = self._create_title_line_manual(title, cfg)

        return [top_line, title_line, bottom_line]

    def print_header(self, title: str, config: HeaderConfig | None = None, **kwargs) -> str:
        """Generate a header string with customizable separators and styling.

        Args:
            title: The title text to display
            config: HeaderConfig object, or None to use defaults
            **kwargs: Override any config values (top_sep, left_sep, etc.)
        """
        local_console = Console()
        cfg: HeaderConfig = config or HeaderConfig()
        for key, value in kwargs.items():
            if hasattr(cfg, key):
                setattr(cfg, key, value)

        if cfg.use_panel:
            panel: Panel = self._create_panel_header(title, cfg)
            output: Align | Panel = Align.center(panel) if cfg.center_align else panel

            if not cfg.return_txt:
                local_console.print(output, style=cfg.overall_style)

            temp_console: Console = Console(file=StringIO(), width=cfg.length)
            temp_console.print(output, style=cfg.overall_style)
            return cast("StringIO", temp_console.file).getvalue()

        header_lines = self._create_manual_header(title, cfg)

        if cfg.center_align:
            header_lines = [Align.center(line) for line in header_lines]

        if not cfg.return_txt:
            local_console.print()
            for line in header_lines:
                local_console.print(line, style=cfg.overall_style)
            local_console.print()
        output_lines: list[str] = [str(line) for line in header_lines]
        return "\n" + "\n".join(output_lines) + "\n"

    def quick_header(self, title: str, style: str = "cyberpunk") -> str:
        """Quick header with predefined styles."""
        styles = {
            "cyberpunk": HeaderConfig(
                top_sep=str(FontStyle.SOLID),
                left_sep=str(FontStyle.RIGHT_ARROWS),
                right_sep=str(FontStyle.LEFT_ARROWS),
                bottom_sep=str(FontStyle.SOLID),
                title_style="bold bright_magenta",
                border_style="bright_cyan",
                separator_style="bright_green",
                overall_style="",
                use_panel=False,
            ),
            "panel": HeaderConfig(title_style="bold bright_magenta", border_style="bright_cyan", use_panel=True),
            "classic": HeaderConfig(),  # Uses defaults
            "minimal": HeaderConfig(top_sep="─", left_sep="", right_sep="", bottom_sep="─", separator_style="dim"),
        }

        config = styles.get(style, HeaderConfig())
        return self.print_header(title, config)


def ascii_header(title: str, print_out: bool = True, **kwargs) -> str:
    """Generate a header string for visual tests.

    Args:
        title: The title to display
        print_out: Whether to print or return the header
        **kwargs: Any HeaderConfig parameters (top_sep, length, etc.)
    """
    config = HeaderConfig(return_txt=not print_out, **kwargs)
    text_helper = TextHelper()
    result = text_helper.print_header(title, config)
    return "" if print_out else result


if __name__ == "__main__":
    top: str = ""
    bottom: str = ""
    left: str = FontStyle.HOLLOW.text
    right: str = FontStyle.HOLLOW.text
    ascii_header(
        "CYBERDYNE BANKING SYSTEM",
        top_sep=top,
        bottom_sep=bottom,
        left_sep=left,
        right_sep=right,
        title_style="red",
        separator_style="black",
        border_style="black",
        print_out=True,
    )

    WORD = "BRAINS"
    text = ""
    console = Console()
    if HAS_PYFIGLET:
        for font in FigletFonts:
            try:
                text = figlet_format(WORD, font=font.value)  # type: ignore[arg-type]
            except Exception as e:
                console.print(f"Error generating font '{font.value}': {e}")
                continue
            # console.print(f"\nFont: {font.value}", style="dim white")
            # console.print(text, style=random_style())
            # text = ""
