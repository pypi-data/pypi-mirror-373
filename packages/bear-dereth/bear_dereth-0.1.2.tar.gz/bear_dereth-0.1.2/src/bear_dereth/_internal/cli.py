# - When you run `python -m bear_dereth` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `bear_dereth.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `bear_dereth.__main__` in `sys.modules`.
from __future__ import annotations

from argparse import ArgumentParser, Namespace
import sys

from bear_dereth._internal._info import _METADATA
from bear_dereth._internal.debug import _print_debug_info
from bear_dereth.constants.enums import ExitCode
from bear_dereth.constants.enums.version_parts import VALID_BUMP_TYPES
from bear_dereth.tools.cli.arg_helpers import CLIArgsType, args_parse
from bear_dereth.tools.versioning import BumpType, cli_bump


def _debug_info(no_color: bool = False) -> ExitCode:
    """CLI command to print debug information."""
    _print_debug_info(no_color=no_color)
    return ExitCode.SUCCESS


def _version(name: bool = False) -> ExitCode:
    """CLI command to get the current version of the package."""
    to_print: str = ""
    if name:
        to_print += _METADATA.name + " "
    to_print += _METADATA.version
    print(to_print)
    return ExitCode.SUCCESS


def _bump(bump_type: BumpType) -> ExitCode:
    """CLI command to bump the version of the package."""
    return cli_bump(b_type=bump_type, package_name=_METADATA.name, ver=_METADATA.version_tuple)


def _get_args(args: CLIArgsType) -> Namespace:
    name: str = _METADATA.name
    parser = ArgumentParser(description=name.capitalize(), prog=name, exit_on_error=False)
    subparser = parser.add_subparsers(dest="command", required=False, help="Available commands")
    subparser.add_parser("version", help="Get the current version of the package")
    debug = subparser.add_parser("debug_info", help="Print debug information")
    debug.add_argument("-n", "--no-color", action="store_true", help="Disable color output")
    bump: ArgumentParser = subparser.add_parser("bump")
    bump.add_argument("bump_type", type=str, choices=VALID_BUMP_TYPES, help="major, minor, or patch")
    return parser.parse_args(args)


@args_parse()
def main(args: CLIArgsType) -> ExitCode:
    """Entry point for the CLI application.

    This function is executed when you type `bear_dereth` or `python -m bear_dereth`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    arguments: Namespace = _get_args(args)
    try:
        if arguments.command == "version":
            return _version()
        if arguments.command == "debug_info":
            return _debug_info()
        if arguments.command == "bump":
            return _bump(bump_type=arguments.bump_type)
        return ExitCode.SUCCESS
    except SystemExit as e:
        if e.code is not None and isinstance(e.code, int):
            return ExitCode(e.code)
        return ExitCode.SUCCESS
    except Exception:
        return ExitCode.FAILURE


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
