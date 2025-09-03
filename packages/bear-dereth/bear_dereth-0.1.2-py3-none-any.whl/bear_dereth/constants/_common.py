"""Shared shell utilities.

``DEFAULT_SHELL`` attempts to locate ``zsh`` on the host using :func:`shutil.which`.
If that fails, ``/bin/sh`` is used instead.
"""

from shutil import which

DEFAULT_SHELL: str = which("zsh") or which("bash") or "/bin/sh"
"""Dynamically detected shell path, falling back to ``/bin/sh``."""

BASH: str | None = which("bash")
"""Path to the Bash shell, falling back to ``/bin/bash`` if not found."""

ZSH: str | None = which("zsh") or which("/bin/zsh")
"""Path to the Zsh shell, falling back to ``/bin/zsh`` if not found."""

SH: str | None = which("sh") or "bin/sh"
"""Path to the Bourne shell, falling back to ``/bin/sh`` if not found."""
