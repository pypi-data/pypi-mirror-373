"""This module provides textio-like classes for various purposes, including a mock TextIO for testing."""

import sys
from typing import Any, Self, TextIO


class MockTextIO(TextIO):
    """A mock TextIO class that captures written output for testing purposes."""

    def __init__(self) -> None:
        """Initialize the mock TextIO."""
        self._buffer: list[str] = []

    def write(self, _s: str, *_) -> None:  # type: ignore[override]
        """Mock write method that appends to the buffer."""
        if _s == "\n":
            return
        self._buffer.append(_s)

    def output_buffer(self) -> list[str]:
        """Get the output buffer."""
        return self._buffer

    def clear(self) -> None:
        """Clear the output buffer."""
        self._buffer.clear()

    def flush(self) -> None:
        """Mock flush method that does nothing."""


class NullFile(TextIO):
    """A class that acts as a null file, discarding all writes."""

    def write(self, _s: str, *_: Any) -> None:  # type: ignore[override]
        """Discard the string written to this null file."""

    def flush(self) -> None:
        """Flush the null file (no operation)."""

    def __enter__(self) -> Self:
        """Enter context manager and return self."""
        return self

    def __exit__(self, *_: object) -> None:
        """Exit context manager (no operation)."""


STDOUT: TextIO = sys.stdout
"""Standard output stream."""
STDERR: TextIO = sys.stderr
"""Standard error stream."""
DEVNULL: TextIO = NullFile()
"""A null file that discards all writes."""

__all__ = [
    "DEVNULL",
    "STDERR",
    "STDOUT",
    "MockTextIO",
    "NullFile",
]
