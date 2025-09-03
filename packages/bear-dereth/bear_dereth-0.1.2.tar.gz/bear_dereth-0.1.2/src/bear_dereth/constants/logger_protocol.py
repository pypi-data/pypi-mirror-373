"""A protocol for logging classes for general use."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LoggerProtocol(Protocol):
    """A protocol for logging classes with extra methods."""

    def debug(self, msg: object, *args, **kwargs) -> None: ...

    def info(self, msg: object, *args, **kwargs) -> None: ...

    def warning(self, msg: object, *args, **kwargs) -> None: ...

    def error(self, msg: object, *args, **kwargs) -> None: ...

    def verbose(self, msg: object, *args, **kwargs) -> None: ...

    def success(self, msg: object, *args, **kwargs) -> None: ...

    def failure(self, msg: object, *args, **kwargs) -> None: ...


@runtime_checkable
class AsyncLoggerProtocol(Protocol):
    """A protocol for asynchronous logging classes."""

    async def debug(self, msg: object, *args, **kwargs) -> None: ...

    async def info(self, msg: object, *args, **kwargs) -> None: ...

    async def warning(self, msg: object, *args, **kwargs) -> None: ...

    async def error(self, msg: object, *args, **kwargs) -> None: ...

    async def verbose(self, msg: object, *args, **kwargs) -> None: ...

    async def success(self, msg: object, *args, **kwargs) -> None: ...

    async def failure(self, msg: object, *args, **kwargs) -> None: ...


# ruff: noqa: D102

Loggers = LoggerProtocol | AsyncLoggerProtocol

__all__ = [
    "AsyncLoggerProtocol",
    "LoggerProtocol",
    "Loggers",
]
