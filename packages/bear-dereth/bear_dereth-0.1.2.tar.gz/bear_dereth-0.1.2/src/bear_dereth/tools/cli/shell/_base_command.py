from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Self

from pydantic import BaseModel, Field

from bear_dereth.constants._common import DEFAULT_SHELL

if TYPE_CHECKING:
    from subprocess import CompletedProcess

    from bear_dereth.constants.logger_protocol import Loggers


class ShellConfig(BaseModel):
    """Configuration for shell commands"""

    shell: str = DEFAULT_SHELL
    cwd: Path = Path.cwd()
    env: dict[str, str] = Field(default=os.environ.copy())  # FIXME: Address security implications
    logger: Loggers | None = Field(default=None)
    verbose: bool = False
    use_shell: bool = True

    model_config = {"arbitrary_types_allowed": True}


class BaseShellCommand[T: str]:
    """Base class for typed shell commands compatible with session systems"""

    command_name: ClassVar[str] = ""

    def __init__(self, *args, **kwargs) -> None:
        self.sub_command: str = kwargs.pop("sub_command", "")
        self.args: tuple[str, ...] = args
        self.suffix = kwargs.get("suffix", "")
        self.result: CompletedProcess[str] | None = None
        self.shell_config: ShellConfig = kwargs.pop("shell_config", ShellConfig(**kwargs))

    def __str__(self) -> str:
        """String representation of the command"""
        return self.cmd

    def value(self, v: str) -> Self:
        """Add value to the export command"""
        self.suffix: str = v
        return self

    @classmethod
    def adhoc(cls, name: str, *args, **kwargs) -> BaseShellCommand:
        """Create an ad-hoc command class for a specific command

        Args:
            name (str): The name of the command to create

        Returns:
            BaseShellCommand: An instance of the ad-hoc command class.
        """
        return type(
            f"AdHoc{name.title()}Command",
            (cls,),
            {"command_name": name},
        )(*args, **kwargs)

    @classmethod
    def sub(cls, s: str, *args, **kwargs) -> Self:
        """Set a sub-command for the shell command"""
        return cls(s, *args, **kwargs)

    @property
    def cmd(self) -> str:
        """Return the full command as a string"""
        cmd_parts: list[str] = [self.command_name, self.sub_command, *self.args]
        cmd_parts: list[str] = [part for part in cmd_parts if part]
        joined: str = " ".join(cmd_parts).strip()
        if self.suffix:
            return f"{joined} {self.suffix}"
        return joined

    def do(self, **kwargs) -> Self:
        """Run the command using subprocess"""
        from ._base_shell import shell_session  # noqa: PLC0415

        shell_config: dict[str, Any] = self.shell_config.model_dump(exclude_none=True)
        if kwargs:
            shell_config.update(kwargs)
        with shell_session(**shell_config) as session:
            result: CompletedProcess[str] = session.add(self.cmd).run()
        if result is not None:
            self.result = result
        return self

    def get_result(self) -> CompletedProcess[str]:
        """Get the result of the command execution"""
        if self.result is None:
            self.do()
        if self.result is None:
            raise RuntimeError("Command execution failed for some reason.")
        return self.result

    def get(self) -> str:
        """Get the result of the command execution"""
        if self.result is None:
            self.do()
        if self.result is None:
            raise RuntimeError("Command execution failed for some reason.")
        return str(self.result.stdout).strip()
