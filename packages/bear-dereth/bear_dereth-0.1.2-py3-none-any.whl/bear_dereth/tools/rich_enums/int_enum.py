"""A module defining a IntEnum with more metadata support."""

from contextlib import suppress
from enum import IntEnum
from typing import Protocol, Self, overload

from bear_dereth.tools.rich_enums.base_value import BaseEnumMixin, BaseValue


class IntProtocol(Protocol):
    """Structural type for objects with int value, text, and default."""

    @property
    def value(self) -> int:
        """An integer value."""
        ...

    @property
    def text(self) -> str:
        """A descriptive text."""
        ...

    @property
    def default(self) -> int:
        """A default integer value."""
        ...


class IntValue(BaseValue[int, int]):
    """A frozen dataclass for holding constant integer values."""

    default: int = 0


class RichIntEnum(IntEnum, BaseEnumMixin):
    """Base class for IntEnums with rich metadata."""

    text: str
    default: int

    def __new__(cls, value: IntProtocol) -> Self:
        """Create a new enum member with the given IntProtocol."""
        obj: Self = int.__new__(cls, value.value)
        obj._value_ = value.value
        obj.text = value.text or ""
        obj.default = value.default
        return obj

    def __int__(self) -> int:
        """Return the integer value of the enum."""
        return self.value

    def __str__(self) -> str:
        """Return a string representation of the enum."""
        return str(self.value)

    @overload
    @classmethod
    def get(cls, value: int | str | Self, default: Self) -> Self: ...
    @overload
    @classmethod
    def get(cls, value: int | str | Self, default: None = None) -> Self | None: ...

    @classmethod
    def get(cls, value: int | str | Self, default: Self | None = None) -> Self | None:
        """Try by instance, then by int value, then by name (exact/CI), then by text."""
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            with suppress(ValueError):
                return cls.from_value(value)
        if isinstance(value, str):
            with suppress(ValueError):
                return cls.from_name(value)
            with suppress(ValueError):
                return cls.from_text(value)
        return default

    @classmethod
    def from_int(cls, code: int) -> Self:
        """Convert an integer to its corresponding enum member."""
        if (member := cls._by_value().get(code)) is not None:
            return member
        raise ValueError(f"Value {code!r} not found in {cls.__name__}")

    @classmethod
    def int_to_text(cls, code: int) -> str:
        """Convert an integer to its text representation."""
        try:
            return cls.from_int(code).text
        except ValueError:
            return "Unknown value"
