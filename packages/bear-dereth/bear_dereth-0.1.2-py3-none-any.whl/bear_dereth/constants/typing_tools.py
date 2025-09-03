"""A set of type aliases and utility functions for type validation and inspection."""

from collections.abc import Callable
from types import NoneType
from typing import Any, Literal, get_args

from bear_dereth.constants.exceptions import ObjectTypeError

LitInt = Literal["int"]
LitFloat = Literal["float"]
LitStr = Literal["str"]
LitBool = Literal["bool"]
LitFalse = Literal[False]
LitTrue = Literal[True]

OptInt = int | None
OptFloat = float | None
OptStr = str | None
OptBool = bool | None
OptStrList = list[str] | None
OptStrDict = dict[str, str] | None


def num_type_params(cls: type) -> int:
    """Get the number of type parameters of a subclass that inherits from a generic class.

    Args:
        cls (object): The class object from which to retrieve the number of type parameters.

    Returns:
        int: The number of type parameters.

    Raises:
        TypeError: If the class does not have type parameters.
        AttributeError: If the class does not have the expected type parameters.
    """
    try:
        args: tuple[Any, ...] = get_args(cls.__orig_bases__[0])
    except (AttributeError, TypeError):
        raise TypeError(f"{cls.__name__} does not have type parameters.") from None
    return len(args)


def type_param(cls: type, index: int = 0) -> type:
    """Get the type parameter of a subclass that inherits from a generic class.

    Args:
        cls (object): The class object from which to retrieve the type parameter.
        index (int): The index of the type parameter to retrieve. Defaults to 0.

    Returns:
        type: The type parameter at the specified index.

    Raises:
        IndexError: If the specified index is out of range for the type parameters.
        TypeError: If the class does not have type parameters.
        AttributeError: If the class does not have the expected type parameters.
    """
    try:
        args: tuple[Any, ...] = get_args(cls.__orig_bases__[0])
    except IndexError:
        raise IndexError(f"Index {index} is out of range for type parameters of {cls.__name__}.") from None
    except (AttributeError, TypeError):
        raise TypeError(f"{cls.__name__} does not have type parameters.") from None
    if args[index] is NoneType:
        raise TypeError(f"Type parameter at index {index} is NoneType for {cls.__name__}.")
    return args[index]


def coerce_to_type[T](val: Any, to_type: Callable[[Any], T]) -> T:
    """Coerce a value to the specified type if possible.

    Args:
        val (Any): The value to coerce.
        to_type (type): The type to which the value should be coerced.

    Returns:
        Any: The coerced value.

    Raises:
        ValueError: If the value cannot be coerced to the specified type.
    """
    try:
        return to_type(val)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Cannot coerce value {val} of type {type(val).__name__} to {to_type.__name__}.") from e


def mapping_to_type[T](mapping: dict[str, Any], key: str, to_type: Callable[[Any], T], default: Any = None) -> T:
    """Get a value from a mapping and coerce it to the specified type if possible.

    Args:
        mapping (dict[str, Any]): The mapping from which to retrieve the value.
        key (str): The key of the value to retrieve.
        to_type (type): The type to which the value should be coerced.
        default (Any): The default value to return if the key is not found. Defaults to None.

    Returns:
        Any: The coerced value.

    Raises:
        ValueError: If the value cannot be coerced to the specified type.
    """
    if key not in mapping:
        if default is not None:
            return coerce_to_type(val=default, to_type=to_type)
        raise KeyError(f"Key {key} not found in mapping and no default provided.")
    return coerce_to_type(val=mapping[key], to_type=to_type)


def validate_type(val: Any, expected: type, exception: type[ObjectTypeError] | None = None) -> None:
    """Validate the type of the given value.

    Args:
        val (Any): The value to validate.
        expected (type): The expected type of the value.
        exception (type[ObjectTypeError] | None): The exception to raise if the type
            does not match. If None, a TypeError is raised.
    """
    if not isinstance(val, expected):
        if exception is None:
            raise TypeError(f"Expected object of type {expected.__name__}, but got {type(val).__name__}.")
        raise exception(expected=expected, received=type(val))
