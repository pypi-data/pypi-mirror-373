"""A set of helper Pydantic models."""

from collections.abc import Callable
from types import SimpleNamespace as Namespace
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DynamicAttrs(BaseModel):
    """A model to hold dynamic attributes in a Namespace."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    root: Namespace = Field(default_factory=Namespace, description="Holder for dynamic attributes.")
    default_fields_: list[str] = Field(default_factory=list, exclude=True, alias="default_fields")

    def model_post_init(self, context: Any) -> None:
        """Initialize default fields in the Namespace."""
        for field in self.default_fields_:
            if not self.has(field):
                self.set(field, {})
        return super().model_post_init(context)

    def has(self, key: str) -> bool:
        """Check if the attribute exists in the Namespace."""
        return hasattr(self.root, key)

    def get(self, key: str, default: Any = None) -> Any:
        """Get the attribute value or return default if not found."""
        return getattr(self.root, key, default)

    def set(self, key: str, value: Any) -> None:
        """Set the attribute value in the Namespace."""
        setattr(self.root, key, value)

    def dump_root(self) -> dict[str, Any]:
        """Dump the model to a dictionary including dynamic attributes."""
        return self.root.__dict__

    def __getattr__(self, key: str) -> Any:
        if not self.has(key):
            raise AttributeError(f"'DynamicAttrs' object has no attribute '{key}'")
        return getattr(self.root, key)

    def __setattr__(self, key: str, value: Any) -> None:
        if key in {"root", "extra"}:
            object.__setattr__(self, key, value)
            return
        setattr(self.root, key, value)


def nullable_string_validator(field_name: str) -> Callable[..., str | None]:
    """Create a validator that converts 'null' strings to None."""

    @field_validator(field_name)
    @classmethod
    def _validate(cls: object, v: str | None) -> str | None:  # noqa: ARG001
        if isinstance(v, str) and v.lower() in ("null", "none", ""):
            return None
        return v

    return _validate
