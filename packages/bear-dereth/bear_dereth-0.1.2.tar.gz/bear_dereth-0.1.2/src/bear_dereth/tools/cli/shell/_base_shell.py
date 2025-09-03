from __future__ import annotations

import asyncio
from collections import deque
from contextlib import asynccontextmanager, contextmanager
from io import StringIO
import os
from pathlib import Path
import shlex
import subprocess
from subprocess import CompletedProcess
from typing import TYPE_CHECKING, Self, override

from bear_dereth.constants._common import DEFAULT_SHELL
from bear_dereth.constants.enums import ExitCode
from bear_dereth.constants.logger_protocol import Loggers  # noqa: TC001

if TYPE_CHECKING:
    from asyncio.streams import StreamReader
    from asyncio.subprocess import Process
    from collections.abc import AsyncGenerator, Callable, Generator, Sequence

    from _typeshed import StrOrBytesPath

    from ._base_command import BaseShellCommand

    _CMD = StrOrBytesPath | Sequence[StrOrBytesPath]


class DefaultPrinter:
    """A simple printer class to use as a default logger"""

    def debug(self, msg: object, *args, **kwargs) -> None:
        print(f"[DEBUG] {msg}", *args, **kwargs)

    def info(self, msg: object, *args, **kwargs) -> None:
        print(f"[INFO] {msg}", *args, **kwargs)

    def warning(self, msg: object, *args, **kwargs) -> None:
        print(f"[WARNING] {msg}", *args, **kwargs)

    def error(self, msg: object, *args, **kwargs) -> None:
        print(f"[ERROR] {msg}", *args, **kwargs)

    def verbose(self, msg: object, *args, **kwargs) -> None:
        print(f"[VERBOSE] {msg}", *args, **kwargs)

    def success(self, msg: object, *args, **kwargs) -> None:
        print(f"[SUCCESS] {msg}", *args, **kwargs)

    def failure(self, msg: object, *args, **kwargs) -> None:
        print(f"[FAILURE] {msg}", *args, **kwargs)


class FancyCompletedProcess(CompletedProcess[str]):
    def __init__(self, args: _CMD, returncode: int, stdout: str | None = None, stderr: str | None = None) -> None:
        """Initialize with custom attributes for better readability"""
        super().__init__(args=args, returncode=returncode, stdout=stdout, stderr=stderr)

    def __repr__(self) -> str:
        """Custom representation for better readability"""
        args: list[str] = [
            f"args={self.args!r}",
            f"returncode={self.returncode!r}",
            f"exit_message={self.exit_message!r}",
            f"stdout={self.stdout!r}" if self.stdout is not None else "",
            f"stderr={self.stderr!r}" if self.stderr is not None else "",
        ]
        return f"{type(self).__name__}({', '.join(filter(None, args))})"

    @property
    def exit_message(self) -> str:
        """Get a human-readable message for the exit code"""
        return ExitCode.from_int(self.returncode).text


class CommandList(deque[CompletedProcess[str]]):
    """A list to hold previous commands with their timestamps and results"""

    def __init__(self, maxlen: int = 10, *args, **kwargs) -> None:
        super().__init__(maxlen=maxlen, *args, **kwargs)  # noqa:  B026

    def add(self, command: CompletedProcess[str]) -> None:
        """Add a command to the list"""
        self.append(command)

    def get(self, index: int) -> CompletedProcess[str] | None:
        """Get a command by index"""
        return self[index] if 0 <= index < len(self) else None

    def get_most_recent(self) -> CompletedProcess[str] | None:
        """Get the most recent command"""
        return self[-1] if self else None


class SimpleShellSession:
    """Simple shell session using subprocess with command chaining"""

    def __init__(
        self,
        env: dict | None = None,
        cwd: Path | str | None = None,
        shell: str = DEFAULT_SHELL,
        logger: Loggers | None = None,
        verbose: bool = False,
        use_shell: bool = True,
    ) -> None:
        self.shell: str = shell
        self.cwd: Path = Path.cwd() if cwd is None else Path(cwd)
        self.env: dict[str, str] = os.environ.copy() if env is None else env
        self.verbose: bool = verbose
        self.use_shell: bool = use_shell
        self.logger: Loggers = self.set_logger(logger)

        self.cmd_buffer: StringIO = StringIO()
        self.previous_commands: CommandList = CommandList()
        self.result: CompletedProcess[str] | None = None

    def set_logger(self, passed_logger: Loggers | None = None) -> Loggers:
        """Set the logger for the session, defaulting to a base logger if none is provided"""
        if passed_logger is not None:
            return passed_logger
        return DefaultPrinter()

    def add_to_env(self, env: dict[str, str], key: str | None = None, value: str | None = None) -> Self:
        """Populate the environment for the session"""
        _env = {}
        if isinstance(env, str) and key is not None and value is not None:
            _env[key] = value
        elif isinstance(env, dict):
            for k, v in env.items():
                _env[k] = v
        self.env.update(_env)
        return self

    def add(self, c: str | BaseShellCommand) -> Self:
        """Add a command to the current session, return self for chaining"""
        self.cmd_buffer.write(str(c))
        return self

    def amp(self, c: str | BaseShellCommand) -> Self:
        """Combine a command with the current session: &&, return self for chaining"""
        if self.empty_history:
            raise ValueError("No command to combine with")
        self.cmd_buffer.write(" && ")
        self.cmd_buffer.write(str(c))
        return self

    def piped(self, c: str | BaseShellCommand) -> Self:
        """Combine a command with the current session: |, return self for chaining"""
        if self.empty_history:
            raise ValueError("No command to pipe from")
        self.cmd_buffer.write(" | ")
        self.cmd_buffer.write(str(c))
        return self

    def _run(self, command: str, **kwargs) -> CompletedProcess[str]:
        """Internal method to run the accumulated command"""
        self.logger.debug(f"Executing: {command}")
        self.next_cmd()
        override = kwargs.pop("override", False)
        common_attrs = {
            "args": command if self.use_shell else shlex.split(command),
            "cwd": self.cwd,
            "env": self.env,
            "shell": bool(self.use_shell),
            "capture_output": True,
        }
        if override:
            common_attrs.update(kwargs)
        self.result = subprocess.run(check=False, text=True, **common_attrs)
        if self.result.returncode != 0:
            self.logger.error(f"Command failed with return code {self.result.returncode} {self.result.stderr.strip()}")
        self.reset_buffer()
        return self.result

    def run(self, cmd: str | BaseShellCommand | None = None, *args, **kwargs) -> CompletedProcess[str]:
        """Run the accumulated command history"""
        if self.empty_history and cmd is None:
            raise ValueError("No commands to run")

        if self.has_history and cmd is not None:
            raise ValueError(
                "If you want to add a command to a chain, use `amp` instead of `run`, `run` is for executing the full command history"
            )

        if self.has_history and cmd is None:
            result: CompletedProcess[str] = self._run(self.cmd, **kwargs)
        elif self.empty_history and cmd is not None:
            self.cmd_buffer.write(f"{cmd} ")
            if args:
                self.cmd_buffer.write(" ".join(map(str, args)))
            result: CompletedProcess[str] = self._run(self.cmd, **kwargs)
        else:
            raise ValueError("Unexpected state")
        self.reset_buffer()
        return result

    @property
    def empty_history(self) -> bool:
        """Check if the command history is empty"""
        return not self.cmd_buffer.getvalue()

    @property
    def has_history(self) -> bool:
        """Check if there is any command in the history"""
        return not self.empty_history

    @property
    def cmd(self) -> str:
        """Return the combined command as a string"""
        if not self.cmd_buffer:
            raise ValueError("No commands have been run yet")
        return (
            f"{self.shell} -c {shlex.quote(self.cmd_buffer.getvalue())}"
            if self.use_shell
            else self.cmd_buffer.getvalue().strip()
        )

    @property
    def returncode(self) -> bool:
        """Return the last command's return code"""
        if self.result is None:
            raise ValueError("No command has been run yet")
        return self.result.returncode == 0

    @property
    def stdout(self) -> str:
        """Return the standard output of the last command"""
        if self.result is None:
            raise ValueError("No command has been run yet")
        return self.result.stdout.strip() if self.result.stdout is not None else "None"

    @property
    def stderr(self) -> str:
        """Return the standard error of the last command"""
        if self.result is None:
            raise ValueError("No command has been run yet")
        return self.result.stderr.strip() if self.result.stderr is not None else "None"

    @property
    def pretty_result(self) -> str:
        """Return a formatted string of the command result"""
        if self.result is None:
            raise ValueError("No command has been run yet")
        return (
            f"Command: {self.result.args}\n"
            f"Return Code: {self.result.returncode}\n"
            f"Standard Output: {self.result.stdout.strip()}\n"
            f"Standard Error: {self.result.stderr.strip()}\n"
        )

    def reset_buffer(self) -> None:
        """Reset the command buffer"""
        self.cmd_buffer.seek(0)
        self.cmd_buffer.truncate(0)

    def reset(self) -> None:
        """Reset the session state"""
        self.previous_commands.clear()
        self.result = None

    def next_cmd(self) -> None:
        """Store the current command in the history before running a new one"""
        if self.result is not None:
            self.previous_commands.add(command=self.result)
            self.result = None

    def get_cmd(self, index: int | None = None) -> CompletedProcess[str] | None:
        """Get a previous command by index or the most recent one if index is None"""
        if index is None:
            return self.previous_commands.get_most_recent()
        return self.previous_commands.get(index)

    def exit(self) -> None:
        """Exit the shell session, resetting state and closing resources"""
        self.reset()
        self.reset_buffer()
        self.cmd_buffer.close()

    def __enter__(self) -> Self:
        """Enter the context manager"""
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Exit the context manager"""
        self.exit()


class AsyncShellSession(SimpleShellSession):
    """Shell session using Popen for more control over the subprocess"""

    def __init__(
        self,
        env: dict[str, str] | None = None,
        cwd: str | None = None,
        shell: str = DEFAULT_SHELL,
        logger: Loggers | None = None,
        verbose: bool = False,
        use_shell: bool = True,
    ) -> None:
        super().__init__(env=env, cwd=cwd, shell=shell, logger=logger, verbose=verbose, use_shell=use_shell)
        self.process: Process | None = None
        self._callbacks: list[Callable[[CompletedProcess], None]] = []

    @override
    async def _run(self, command: str, **kwargs) -> Process:  # type: ignore[override]
        """Run the command using Popen for better control"""
        self.logger.debug(f"Executing: {command}")
        self.next_cmd()

        if self.use_shell:
            self.process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd,
                env=self.env,
                **kwargs,
            )
        else:
            command_args: list[str] = shlex.split(command)
            self.process = await asyncio.create_subprocess_exec(
                *command_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd,
                env=self.env,
                **kwargs,
            )
        return self.process

    @override
    async def run(self, cmd: str | BaseShellCommand | None = None, *args, **kwargs) -> Process:  # type: ignore[override]
        """Async version of run that returns Process for streaming"""
        if self.empty_history and cmd is None:
            raise ValueError("No commands to run")

        if self.has_history and cmd is not None:
            raise ValueError("Use `amp` to chain commands, not `run`")
        if self.has_history and cmd is None:
            command: str = self.cmd
        elif self.empty_history and cmd is not None:
            self.cmd_buffer.write(f"{cmd}")
            if args:
                self.cmd_buffer.write(" ".join(map(str, args)))
            command: str = self.cmd
        else:
            raise ValueError("Unexpected state")
        process: Process = await self._run(command, **kwargs)
        return process

    async def communicate(self, stdin: str = "") -> CompletedProcess[str]:
        """Communicate with the process, sending input and waiting for completion"""
        if self.process is None:
            raise ValueError("No process has been started yet")
        bytes_stdin: bytes = stdin.encode("utf-8") if isinstance(stdin, str) else stdin

        stdout, stderr = await self.process.communicate(input=bytes_stdin)
        return_code: int = await self.process.wait()

        self.result = FancyCompletedProcess(
            args=self.cmd,
            returncode=return_code,
            stdout=stdout.decode() if stdout else "",
            stderr=stderr.decode() if stderr else "",
        )
        if return_code != 0:
            self.logger.error(f"Command failed with return code {return_code} {stderr.strip()}")
        for callback in self._callbacks:
            callback(self.result)
        await self.after_process()
        return self.result

    @staticmethod
    async def read_stream(stream: StreamReader) -> AsyncGenerator[str]:
        while True:
            try:
                line: bytes = await stream.readline()
                if not line:  # EOF
                    break
                yield line.decode("utf-8").rstrip("\n")
            except Exception:
                break

    async def stream_stdout(self) -> AsyncGenerator[str]:
        """Stream output line by line as it comes"""
        if self.process is None:
            raise ValueError("No process has been started yet")
        if not self.process.stdout:
            raise ValueError("Process has no stdout")

        async for line in self.read_stream(self.process.stdout):
            yield line

    async def stream_stderr(self) -> AsyncGenerator[str]:
        """Stream error output line by line as it comes"""
        if self.process is None:
            raise ValueError("No process has been started yet")
        if not self.process.stderr:
            raise ValueError("Process has no stderr")
        async for line in self.read_stream(self.process.stderr):
            yield line

    async def after_process(self) -> None:
        """Run after process completion, can be overridden for custom behavior"""
        self.process = None
        self._callbacks.clear()
        self.reset_buffer()

    def on_completion(self, callback: Callable[[CompletedProcess[str]], None]) -> None:
        """Add callback for when process completes"""
        self._callbacks.append(callback)

    @property
    def is_running(self) -> bool:
        """Check if process is still running"""
        return self.process is not None and self.process.returncode is None


@contextmanager
def shell_session(shell: str = DEFAULT_SHELL, **kwargs) -> Generator[SimpleShellSession]:
    """Context manager for simple shell sessions"""
    session = SimpleShellSession(shell=shell, **kwargs)
    try:
        yield session
    finally:
        session.exit()


@asynccontextmanager
async def async_shell_session(shell: str = DEFAULT_SHELL, **kwargs) -> AsyncGenerator[AsyncShellSession]:
    """Asynchronous context manager for shell sessions"""
    session = AsyncShellSession(shell=shell, **kwargs)
    try:
        yield session
    finally:
        session.exit()
