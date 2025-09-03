"""A module defining StrEnum with rich metadata support."""

from contextlib import suppress
from enum import StrEnum
from typing import Protocol, Self, overload

from bear_dereth.tools.rich_enums.base_value import BaseEnumMixin, BaseValue


class StrProtocol(Protocol):
    """A protocol for objects that have value, text, and default attributes."""

    @property
    def value(self) -> str:
        """A string value."""
        ...

    @property
    def text(self) -> str:
        """A descriptive text."""
        ...

    @property
    def default(self) -> str:
        """A default string value."""
        ...


class StrValue(BaseValue[str, str]):
    """A frozen dataclass for holding constant string values."""

    default: str = ""


class RichStrEnum(StrEnum, BaseEnumMixin):
    """Base class for StrEnums with rich metadata."""

    text: str
    default: str

    def __new__(cls, value: StrProtocol) -> Self:
        """Create a new enum member with the given StrProtocol."""
        obj: Self = str.__new__(cls, value.value)
        obj._value_ = value.value
        obj.text = value.text or ""
        obj.default = value.default
        return obj

    def __str__(self) -> str:
        """Return a string representation of the enum."""
        return self.value

    @overload
    @classmethod
    def get(cls, value: str | Self, default: Self) -> Self: ...

    @overload
    @classmethod
    def get(cls, value: str | Self, default: None = None) -> None: ...

    @classmethod
    def get(cls, value: str | Self, default: Self | None = None) -> Self | None:
        """Try by instance, then by value, then by name, then by text."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            with suppress(ValueError):
                return cls.from_value(value)
            with suppress(ValueError):
                return cls.from_name(value)
            with suppress(ValueError):
                return cls.from_text(value)
        return default

    @classmethod
    def from_name(cls, name: str) -> Self:
        """Convert a string name to its corresponding enum member."""
        if (member := cls._by_name().get(name)) is not None:
            return member
        for k, member in cls._by_name().items():
            if k.casefold() == name.casefold():
                return member
        raise ValueError(f"Name {name!r} not found in {cls.__name__}")
