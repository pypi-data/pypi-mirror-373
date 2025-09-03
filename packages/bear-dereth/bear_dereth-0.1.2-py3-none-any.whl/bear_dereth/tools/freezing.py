"""Utilities for making objects immutable and hashable."""

from collections.abc import Callable
from typing import ClassVar, NoReturn, Self, overload

from pydantic import BaseModel, ConfigDict, Field

from bear_dereth.constants.typing_tools import LitFalse, LitTrue

# ruff: noqa: ARG002 ANN001

NoReturnCall = Callable[..., NoReturn]
AllowableTypes = dict | list | set


class FrozenDict(dict):
    """An immutable dictionary.

    This is used to generate stable hashes for queries that contain dicts.
    Usually, Python dicts are not hashable because they are mutable. This
    class removes the mutability and implements the ``__hash__`` method.
    """

    def __hash__(self) -> int:  # type: ignore[override]
        """Calculate the has by hashing a tuple of all dict items"""
        return hash(tuple(sorted(self.items())))

    def _immutable(self, *args, **kws) -> NoReturn:
        """Disable any method that would modify the dict."""
        raise TypeError("object is immutable")

    __setitem__: NoReturnCall = _immutable
    __delitem__: NoReturnCall = _immutable
    clear: NoReturnCall = _immutable
    setdefault: NoReturnCall = _immutable  # type: ignore[override]
    popitem: NoReturnCall = _immutable

    def update(self, e=None, **f) -> NoReturn:
        """Disable update method."""
        raise TypeError("object is immutable")

    def pop(self, k, d=None) -> NoReturn:
        """Disable pop method."""
        raise TypeError("object is immutable")


@overload
def freeze(obj: dict) -> FrozenDict: ...
@overload
def freeze(obj: list) -> tuple: ...
@overload
def freeze(obj: set) -> frozenset: ...
@overload
def freeze(obj: object) -> object: ...


def freeze(obj: AllowableTypes | object) -> FrozenDict | tuple | frozenset | object:
    """Freeze an object by making it immutable and thus hashable.

    Args:
        obj (AllowableTypes): The object to freeze. Can be a dict, list, or set.

    Returns:
        FrozenDict | tuple | frozenset | object: The frozen version of the object.

    Note:
        This function only handles dicts, lists, and sets. All other objects are returned as
        is without modification.

        If the input is a dict, it is converted to a ``FrozenDict``.
        If the input is a list, it is converted to a tuple.
        If the input is a set, it is converted to a ``frozenset``.
        Other types are returned unchanged.
    """
    if isinstance(obj, dict):
        return FrozenDict((k, freeze(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return tuple(freeze(el) for el in obj)
    if isinstance(obj, set):
        return frozenset(obj)
    return obj


class FrozenModel(BaseModel):
    """A frozen Pydantic model that is immutable and hashable."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    cacheable: bool = Field(default=True, exclude=True)

    def get_hash(self) -> int:
        """Get the hash of the model based on its frozen representation."""
        return hash(self.model_dump())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FrozenModel):
            return NotImplemented
        return self.frozen == other.frozen

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, FrozenModel):
            return NotImplemented
        return self.frozen != other.frozen

    def __hash__(self) -> int:
        if not self.cacheable:
            raise TypeError("This HashValue is not cacheable")
        return self.get_hash()

    @classmethod
    def not_cacheable(cls) -> Self:
        """Mark this hash value as not cacheable."""
        return cls(cacheable=False)

    @property
    def frozen(self) -> FrozenDict:
        """Get a frozen representation of the model."""
        return self.model_dump(frozen=True)

    def frozen_dump(self) -> FrozenDict:
        """Dump the model to a frozen dictionary."""
        return self.model_dump(frozen=True)

    @overload
    def model_dump(self, frozen: LitTrue = True, *args, **kwargs) -> FrozenDict: ...

    @overload
    def model_dump(self, freeze: LitFalse, *args, **kwargs) -> dict: ...

    def model_dump(self, frozen: bool = True, *args, **kwargs) -> dict | FrozenDict:  # type: ignore[override]
        """Dump the model to a dictionary or frozen dictionary.

        Args:
            frozen (bool, optional): Whether to return a frozen dictionary. Defaults to False.
            *args: Additional positional arguments for Pydantic's model_dump.
            **kwargs: Additional keyword arguments for Pydantic's model_dump.

        Returns:
            dict | FrozenDict: The model as a dictionary or frozen dictionary.
        """
        if not frozen:
            return super().model_dump(*args, **kwargs)
        return freeze(super().model_dump(*args, **kwargs))


class BaseNotCacheable(BaseModel):
    """A singleton representing a non-cacheable value."""

    _instance: ClassVar[Self | None] = None

    model_config = ConfigDict(frozen=True)
    cacheable: bool = Field(default=False, exclude=True, frozen=True)

    def __new__(cls) -> Self:
        """Ensure only one instance of BaseNotCacheable exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            super(BaseNotCacheable, cls._instance).__init__()
        return cls._instance

    def __init__(self) -> None:
        """Cannot reinitialize the singleton."""

    def __hash__(self) -> int:
        raise TypeError("This object is not cacheable")
