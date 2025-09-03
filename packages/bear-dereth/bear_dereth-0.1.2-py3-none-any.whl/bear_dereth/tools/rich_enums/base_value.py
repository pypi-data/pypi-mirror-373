"""A module defining a base class for holding constant values of various types for use in specialized enums."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import cache
from types import MappingProxyType
from typing import Protocol, Self


@dataclass(frozen=True)
class BaseValue[T, T2]:
    """A frozen dataclass for holding constant values of any type."""

    value: T
    text: str
    meta: T2 = field(init=False)
    default: T | None = None


class BaseProtocol[T, T2](Protocol):
    """A protocol for objects that have value, text, and default attributes."""

    @property
    def value(self) -> T:
        """A value of type T."""
        ...

    @property
    def text(self) -> str:
        """A descriptive text."""
        ...

    @property
    def default(self) -> T | None:
        """A default value of type T."""
        ...


class BaseEnumMixin(Enum):
    """Base class for IntEnums with rich metadata."""

    text: str

    @classmethod
    @cache
    def _by_value(cls) -> MappingProxyType[object, Self]:
        return MappingProxyType({member.value: member for member in cls})

    @classmethod
    @cache
    def _by_name(cls) -> MappingProxyType[str, Self]:
        return MappingProxyType({member.name: member for member in cls})

    @classmethod
    @cache
    def _by_text(cls) -> MappingProxyType[str, Self]:
        return MappingProxyType({member.text: member for member in cls})

    @classmethod
    @cache
    def keys(cls) -> tuple[str, ...]:
        """Return a tuple of all enum member names."""
        return tuple(member.name for member in cls)

    @classmethod
    @cache
    def values(cls) -> tuple[Self, ...]:
        """Return a tuple of all enum members."""
        return tuple(cls)

    @classmethod
    @cache
    def items(cls) -> tuple[tuple[str, Self], ...]:
        """Return a tuple of (name, member) pairs."""
        return tuple((member.name, member) for member in cls)

    @classmethod
    def from_value(cls, value: object) -> Self:
        """Convert a value to its corresponding enum member."""
        if (member := cls._by_value().get(value)) is not None:
            return member
        raise ValueError(f"Value {value!r} not found in {cls.__name__}")

    @classmethod
    def from_name(cls, name: str) -> Self:
        """Convert a string name to its corresponding enum member."""
        if (member := cls._by_name().get(name)) is not None:
            return member
        for k, member in cls._by_name().items():
            if k.casefold() == name.casefold():
                return member
        raise ValueError(f"Name {name!r} not found in {cls.__name__}")

    @classmethod
    def from_text(cls, text: str) -> Self:
        """Convert a string text to its corresponding enum member."""
        if (member := cls._by_text().get(text)) is not None:
            return member
        raise ValueError(f"Text {text!r} not found in {cls.__name__}")
