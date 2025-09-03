"""Helper functions and decorators for handling command line arguments in functions."""

from collections.abc import Callable
from functools import wraps
import inspect
from inspect import BoundArguments, Signature
import sys
from typing import Annotated

ArgsType = Annotated[list[str] | None, "ArgsType: A list of command line arguments or None to use sys.argv[1:]"]
"""A type alias for when command line arguments may be passed in or None to use sys.argv[1:]."""
CLIArgsType = Annotated[list[str], "CLIArgsType: A list of command line arguments specifically for CLI usage"]
"""A type alias for when command line arguments are expected to be passed in."""


def args_handler(args: ArgsType = None) -> list[str]:
    """A simple function to return command line arguments or a provided list of arguments.

    Args:
        args (list[str] | None): A list of arguments to return. If None, it will return sys.argv[1:].

    Returns:
        list[str]: The list of command line arguments.
    """
    return sys.argv[1:] if args is None else args


def args_parse[ReturnType](
    param_name: str = "args",
    handler: Callable[..., ReturnType] = args_handler,
):
    """A decorator factory to automatically inject command line arguments.

    Args:
        param_name (str): The name of the parameter to inject the arguments into. Default is
            "args".
        handler (Callable[..., ReturnType] | None): A custom handler function to retrieve the
            arguments. If None, it will use the default args_handler function.

    Returns:
        Callable[..., Callable[..., T]]: A decorator that injects command line arguments into the
            specified parameter if it is not already provided.
    """

    def decorator[T](func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            sig: Signature = inspect.signature(func)
            if param_name in sig.parameters and param_name not in kwargs:
                try:
                    bound: BoundArguments = sig.bind_partial(*args, **kwargs)
                    if param_name not in bound.arguments:
                        kwargs[param_name] = handler()
                except TypeError:
                    kwargs[param_name] = handler()
            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["ArgsType", "CLIArgsType", "args_parse"]
