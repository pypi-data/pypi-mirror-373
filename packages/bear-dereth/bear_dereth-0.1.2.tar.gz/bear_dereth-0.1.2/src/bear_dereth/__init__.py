"""Bear Dereth package.

A set of common tools for various bear projects.
"""

from bear_dereth._internal.cli import main
from bear_dereth._internal.debug import _METADATA

__version__: str = _METADATA.version

__all__: list[str] = ["_METADATA", "__version__", "main"]
