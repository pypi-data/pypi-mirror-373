"""A class for holding constant variable values of various types within an enum."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from pydantic import BaseModel

from bear_dereth.tools.rich_enums.base_value import BaseValue
from bear_dereth.tools.rich_enums.str_enum import RichStrEnum

if TYPE_CHECKING:
    from collections.abc import Callable


class VariableType[T](BaseModel):
    """A Pydantic model for variable metadata."""

    parser: Callable[[str], T]  # Function to parse the variable value
    description: str  # Description of the variable
    required: bool = False  # Whether the variable is required
    default: Any = None  # Default value if not provided


@dataclass(frozen=True)
class VariableValue[T](BaseValue[str, T]):
    """A frozen class for holding constant variable values."""

    value: str
    text: str
    meta: T

    def __getattr__(self, item: str) -> Any:
        """Allow access to attributes directly from the model."""
        if hasattr(self.meta, item):
            return getattr(self.meta, item)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")


class VariableEnum(RichStrEnum):
    """Base class for Enums with variable values."""

    meta: Any

    def __new__(cls, value: VariableValue) -> Self:
        """Create a new enum member with the given VariableValue."""
        obj: Self = str.__new__(cls, value.value)
        obj._value_ = value.value
        obj.text = value.text or ""
        obj.meta = value
        return obj

    def __getattr__(self, item: str) -> Any:
        """Allow access to metadata attributes directly from the enum member."""
        if self.meta and hasattr(self.meta, item):
            return getattr(self.meta, item)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __str__(self) -> str:
        """Return a string representation of the enum."""
        return self.value


if __name__ == "__main__":
    from rich import inspect

    # ruff: noqa: S101

    if TYPE_CHECKING:

        class MetaMixin:
            """A mixin for type checking the meta attribute."""

            description: str
            parser: Callable[[str], int]
            required: bool
            default: Any
            extra: str
    else:
        # Runtime - empty class
        class MetaMixin:
            """A mixin for runtime to avoid type checking issues."""

    class MyVariableMeta(VariableType):
        """Example metadata class for a variable."""

        parser: Callable[[str], int] = int
        description: str = "An integer variable"
        required: bool = True
        default: int = 42
        extra: str = "extra attribute"

    class MyVariableEnum(MetaMixin, VariableEnum):
        """A variable enum with metadata."""

        meta: MyVariableMeta

        EXAMPLE = VariableValue(value="example", text="Example Variable", meta=MyVariableMeta())
        EXAMPLE2 = VariableValue(value="example2", text="Another Variable", meta=MyVariableMeta())

    inspect(MyVariableEnum, all=True)
    assert hasattr(MyVariableEnum, "__members__")

    assert str(MyVariableEnum.EXAMPLE) == "example"
    assert MyVariableEnum.EXAMPLE.description == "An integer variable"
    print(MyVariableEnum.EXAMPLE.meta.extra)
