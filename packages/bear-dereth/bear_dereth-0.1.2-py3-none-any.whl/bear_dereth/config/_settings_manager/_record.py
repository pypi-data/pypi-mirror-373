from datetime import datetime
from typing import Any, cast

from pydantic import Field

from bear_dereth.config._settings_manager._common import Document, TypeList, ValueType
from bear_dereth.tools.freezing import FrozenModel


def get_timestamp() -> int:
    """Get the current timestamp in milliseconds since epoch."""
    return int(datetime.now(tz=datetime.now().astimezone().tzinfo).timestamp() * 1000)


class SettingsRecord[Value_T: ValueType](FrozenModel):
    """Pydantic model for a settings record."""

    key: str = Field(default=...)
    value: Value_T = Field(default=...)
    type: TypeList = Field(default="null")

    def model_post_init(self, context: Any) -> None:
        """Post-initialization to set the type based on the value."""
        if isinstance(self.value, bool):
            self.type = "boolean"
        elif isinstance(self.value, int):
            self.type = "number"
        elif isinstance(self.value, float):
            self.type = "float"
        elif isinstance(self.value, str):
            self.type = "string"
        else:
            self.type = "null"
        super().model_post_init(context)

    def __hash__(self) -> int:
        """Hash based on a frozen representation of the model."""
        return self.get_hash()

    def get_document(self) -> Document:
        """Get a dictionary representation of the record."""
        return cast("Document", self.model_dump(frozen=False))  # type: ignore[return-value]
