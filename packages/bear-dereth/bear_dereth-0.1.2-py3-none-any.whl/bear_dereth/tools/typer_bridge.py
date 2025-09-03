"""A simple bridge for augmenting Typer with alias support and command execution for interactive use."""

from collections.abc import Callable
from functools import cached_property
import shlex
from typing import Any

from pydantic import BaseModel
from rich.console import Console

try:
    from typer import Context, Exit, Typer  # type: ignore[import]
    from typer.models import CommandInfo  # type: ignore[import]
except ImportError as e:
    raise ImportError("Typer is required for TyperBridge. Please install it via 'uv pip install typer'") from e


class CommandMeta(BaseModel):
    """Metadata for a Typer command."""

    name: str
    help: str
    hidden: bool


def get_command_meta(command: CommandInfo) -> CommandMeta:
    """Extract metadata from a Typer command."""
    return CommandMeta(
        name=command.name or (command.callback.__name__ if command.callback else "unknown"),
        help=(command.callback.__doc__ if command.callback else None) or "No description available",
        hidden=command.hidden,
    )


class TyperBridge:
    """Simple bridge for Typer command execution."""

    def __init__(
        self,
        typer_app: Typer,
        console: Any,
        is_primary: bool = False,
    ) -> None:
        """Initialize the TyperBridge with a Typer app instance.

        Args:
            typer_app (Typer): The Typer application instance to bridge
            console (Any): The console or logger to use for output, it will use a
                Console instance if not provided.
            is_primary (bool): Whether to use directly instead of using the typer decorator to define commands.
        """
        self.app: Typer = typer_app
        self.console: Any = console or Console()
        self.is_primary: bool = is_primary
        self.ignore_list: list[str] = []

    def command(
        self,
        *name: str,
        ignore: bool = False,
        usage_text: str = "",
        **kwargs,
    ):
        """Decorator to register a command with optional aliases and ignore flag."""

        def decorator[T](func: Callable[..., T]) -> Callable[..., T]:
            if usage_text:
                func.__doc__ = (func.__doc__ or "") + f" | Usage: {usage_text}"

            names: list[str] = [*name]

            if self.is_primary:
                primary_name: str = names.pop(0) if names else func.__name__
                self.app.command(name=primary_name, **kwargs)(func)

            for alias in names:
                self.app.command(name=alias, hidden=True)(func)

            if ignore:
                self.ignore_list.append(func.__name__)
                for alias in [*name]:
                    self.ignore_list.append(alias)

            return func

        return decorator

    def callback(self, **kwargs):
        """Decorator to register a callback function for the Typer app.

        This decorator checks if the invoked subcommand is in the ignore list
        and skips execution if it is. This is useful for ignoring certain commands
        that are registered but should be run differently or not at all.
        It should be used when Typer is NOT the primary command handler.
        """

        def decorator[T](func: Callable[..., T]) -> Callable[..., T | None]:
            def wrapper(ctx: Context) -> T | None:
                if ctx.invoked_subcommand and ctx.invoked_subcommand in self.ignore_list:
                    return None
                return func(ctx)

            self.app.callback(**kwargs)(wrapper)
            return wrapper

        return decorator

    def _exception(self, msg: object, e: Exception) -> None:
        """Raise a Typer Exit exception with the given message."""
        if isinstance(self.console, Console):
            self.console.print(f"[red]{msg} {e}[/red]")
        else:
            self.console.error(f"{msg}", exc_info=True)

    def echo(self, msg: str, style: str | None = None) -> None:
        """Echo a message to the console."""
        if isinstance(self.console, Console):
            self.console.print(msg, style=style)
        else:
            self.console.info(msg)

    def execute_command(self, command_string: str) -> bool:
        """Execute command via Typer. Return True if successful."""
        try:
            parts: list[str] = shlex.split(command_string.strip())
            if not parts:
                return False
            self.app(parts, standalone_mode=False)
            return True
        except Exit:
            return True
        except Exception as e:
            self._exception(f"Error executing command: '{command_string}'", e)
            return False

    @cached_property
    def command_meta(self) -> dict[str, CommandMeta]:
        """Cached property to hold command metadata."""
        command_meta: dict[str, CommandMeta] = {}
        for cmd in self.app.registered_commands:
            cmd_meta: CommandMeta = get_command_meta(command=cmd)
            command_meta[cmd_meta.name] = cmd_meta
        return command_meta

    @cached_property
    def non_hidden_command_meta(self) -> dict[str, CommandMeta]:
        """Cached property to hold non-hidden command metadata."""
        return {name: meta for name, meta in self.command_meta.items() if not meta.hidden}

    def get_all_command_info(self, show_hidden: bool = False) -> dict[str, CommandMeta]:
        """Get all command information from the Typer app."""
        if not show_hidden:
            return self.non_hidden_command_meta
        return self.command_meta

    def get_command_info(self, command_name: str) -> CommandMeta | None:
        """Get metadata for a specific command."""
        return self.command_meta.get(command_name)
