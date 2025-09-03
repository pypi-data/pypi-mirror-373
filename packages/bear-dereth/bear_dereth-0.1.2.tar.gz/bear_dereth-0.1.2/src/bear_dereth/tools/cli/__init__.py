"""A set of command-line interface (CLI) utilities."""

from bear_dereth.constants._common import DEFAULT_SHELL

from .commands import GitCommand, OPShellCommand, UVShellCommand
from .shell._base_command import BaseShellCommand
from .shell._base_shell import SimpleShellSession, shell_session

__all__ = [
    "DEFAULT_SHELL",
    "BaseShellCommand",
    "GitCommand",
    "OPShellCommand",
    "SimpleShellSession",
    "UVShellCommand",
    "shell_session",
]
