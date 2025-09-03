"""Function Response Class for handling function call results."""

from __future__ import annotations

from subprocess import CompletedProcess
from typing import TYPE_CHECKING, Annotated, Any, Self, overload

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from bear_dereth.constants.logger_protocol import Loggers  # noqa: TC001 # DO NOT REMOVE #
from bear_dereth.models.helpers import DynamicAttrs
from bear_dereth.tools.async_helpers import create_async_task, is_async

if TYPE_CHECKING:
    from collections.abc import Callable

    from bear_dereth.constants.typing_tools import LitFalse, LitTrue


def log_task(strings: list[str], log_func: Callable) -> None:
    """Helper to log messages."""
    for msg in strings:
        log_func(msg)


async def log_task_async(output: list[str], log_func: Callable) -> None | Any:
    """Helper to log messages with async."""
    for msg in output:
        await log_func(msg)


class FunctionResponse(BaseModel):
    """A class to represent the response of a function call, including success status, content, and error messages."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str | None = Field(default=None, description="Name of the function or task")
    returncode: Annotated[int, Field(ge=0, lt=1000)] = 0
    content: list[str] = Field(default=[], description="Content returned by the function call")
    error: list[str] = Field(default=[], description="Error message if the function call failed")
    logger: Loggers | None = Field(default=None, description="Logger instance for logging messages.", exclude=True)
    dynamic_: DynamicAttrs = Field(default=DynamicAttrs(default_fields=["extra", "sub_tasks"]), exclude=True)

    @field_validator("content", "error", mode="before")
    @classmethod
    def validate_list_of_strings(cls, value: str | list[str] | Any) -> list[str]:
        """Ensure content and error are lists of strings."""
        if isinstance(value, str):
            return [value] if value else []
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return [item for item in value if item]
        raise TypeError("Content and error must be a string or a list of strings.")

    def __repr__(self) -> str:
        """Return a string representation of Response."""
        fields: dict[str, Any] = {
            "name": self.name,
            "content": ", ".join(self.content) if self.content else None,
            "error": ", ".join(self.error) if self.error else None,
            "success": self.success,
            "returncode": self.returncode if self.returncode != 0 else None,
            "extra": self.extra if self.extra else None,
            "sub_tasks": self.sub_tasks if self.sub_tasks else None,
        }
        return f"Response({', '.join([f'{k}={v!r}' for k, v in fields.items() if v is not None])})"

    def __str__(self) -> str:
        """Return a string representation of Response."""
        return self.__repr__()

    def __setattr__(self, key: str, value: Any) -> None:
        if key in FunctionResponse.model_fields or key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            self.dynamic_.set(key, value)

    def __getattr__(self, key: str) -> Any:
        if self.dynamic_.has(key):
            return self.dynamic_.get(key)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{key}'")

    def _dump_root(self) -> dict[str, Any]:
        """Dump the dynamic attributes to a dictionary."""
        return self.dynamic_.dump_root()

    def _add_sub_task(self, name: str, res: FunctionResponse) -> None:
        """Append a sub-task to the sub_tasks list."""
        self.sub_tasks[name] = res

    def _add_to_extra(self, value: dict) -> None:
        """Add a key-value pair to the extra dictionary."""
        self.extra.update(value)

    @computed_field
    @property
    def success(self) -> bool:
        """Check if the response indicates success."""
        return self.returncode == 0 and not bool(self.error)

    @property
    def extra(self) -> dict[str, Any]:
        """Get the extra dictionary."""
        return self.dynamic_.get("extra", {})

    @property
    def sub_tasks(self) -> dict[str, FunctionResponse]:
        """Get the list of sub-tasks."""
        return self.dynamic_.get("sub_tasks", {})

    @property
    def content_number(self) -> int:
        """Get the number of content items."""
        return len(self.content)

    @property
    def error_number(self) -> int:
        """Get the number of error items."""
        return len(self.error)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str | Any) -> str | None:
        """Ensure name is a string, lowercased, and without spaces."""
        if value is None:
            return value
        if not isinstance(value, str):
            try:
                value = str(value)
            except Exception as e:
                raise TypeError(f"Name must be a string, got {type(value).__name__}.") from e
        return value.lower().replace(" ", "_")

    @classmethod
    def from_process(cls, process: CompletedProcess[str], **kwargs) -> Self:
        """Create a FunctionResponse from a CompletedProcess object."""
        returncode: int = process.returncode if process.returncode is not None else 0
        content: str = process.stdout.strip() if process.stdout else ""
        error: str = process.stderr.strip() if process.stderr else ""

        if returncode == 0 and not content and error:  # Some processes return empty stdout on success
            error, content = content, error
        return cls().add(returncode=returncode, content=content, error=error, **kwargs)

    def sub_task(
        self,
        name: str | None = None,
        logger: Loggers | None = None,
        content: str | list[str] | None = None,
        error: str | list[str] | None = None,
        extra: dict[str, Any] | None = None,
        returncode: int = 0,
        log_output: bool = False,
    ) -> Self:
        """Add a sub-task response to the FunctionResponse."""
        res = FunctionResponse(name=name, logger=logger or self.logger)
        res.add(content=content, error=error, returncode=returncode, log_output=log_output, extra=extra)
        num_sub: int = len(self.sub_tasks) + 1
        self._add_sub_task(name or f"sub_task_{num_sub}", res)
        return self.add(content=res)

    def successful(
        self,
        content: str | list[str] | CompletedProcess[str] | FunctionResponse,
        error: str | list[str] | None = None,
        returncode: int = 0,
        **kwargs,
    ) -> Self:
        """Set the response to a success state with optional content."""
        self.add(content=content, error=error, returncode=returncode, **kwargs)
        return self

    def fail(
        self,
        content: str | list[str] | CompletedProcess[str] | None = None,
        error: str | list[str] | None = None,
        **kwargs,
    ) -> Self:
        """Set the response to a failure state with an error message."""
        self.add(content=content, error=error, returncode=1, **kwargs)
        return self

    def _add_item(self, item: str, target_list: list[str]) -> None:
        """Append an item to the target list if not empty."""
        target_list.append(item) if item != "" else None

    def _add_to_list(self, items: str | list[str], target_list: list[str], name: str | None = None) -> None:
        """Append items to the target list with optional name prefix."""
        try:
            if isinstance(items, list):
                for item in items:
                    self._add_item(f"{name}: {item}" if name else item, target_list)
            elif isinstance(items, str):
                self._add_item(f"{name}: {items}" if name else items, target_list)
        except Exception as e:
            raise ValueError(f"Failed to add items: {e!s}") from e

    def _add_content(self, content: str | list[str], name: str | None = None) -> None:
        """Add content to the FunctionResponse content list."""
        return self._add_to_list(items=content, target_list=self.content, name=name)

    def _add_error(self, error: str | list[str], name: str | None = None) -> None:
        """Add error messages to the FunctionResponse error list."""
        return self._add_to_list(items=error, target_list=self.error, name=name)

    def _handle_function_response(self, func_response: FunctionResponse) -> None:
        """Handle a FunctionResponse object and update the current response."""
        if func_response:
            self._add_to_extra(value=func_response.extra)
        self._add_content(func_response.content, name=func_response.name)
        self._add_error(func_response.error, name=func_response.name)

    def _handle_completed_process(self, result: CompletedProcess[str]) -> None:
        """Handle a CompletedProcess object and update the FunctionResponse."""
        self._add_content(result.stdout.strip())
        self._add_error(result.stderr.strip())
        self.returncode = result.returncode

    def _handle_content(self, content: str | list[str] | CompletedProcess[str] | FunctionResponse | None) -> None:
        """Handle different types of content and update the FunctionResponse."""
        return (
            self._handle_function_response(func_response=content)
            if isinstance(content, FunctionResponse)
            else self._handle_completed_process(result=content)
            if isinstance(content, CompletedProcess)
            else self._add_to_list(content, self.content)
            if isinstance(content, (str | list))
            else None
        )

    @overload
    def add(
        self,
        content: str | list[str] | CompletedProcess[str] | FunctionResponse | None = None,
        error: str | list[str] | None = None,
        returncode: int = 0,
        log_output: bool = False,
        extra: dict | None = None,
        *,
        to_dict: LitTrue,
    ) -> dict[str, Any]: ...

    @overload
    def add(
        self,
        content: str | list[str] | CompletedProcess[str] | FunctionResponse | None = None,
        error: str | list[str] | None = None,
        returncode: int = 0,
        log_output: bool = False,
        extra: dict | None = None,
        *,
        to_dict: LitFalse = False,
    ) -> Self: ...

    def add(
        self,
        content: str | list[str] | CompletedProcess[str] | FunctionResponse | None = None,
        error: str | list[str] | None = None,
        returncode: int = 0,
        log_output: bool = False,
        extra: dict | None = None,
        *,
        to_dict: bool = False,
    ) -> Self | dict[str, Any]:
        """Append additional content to the existing content."""
        self.returncode = returncode if returncode else self.returncode
        try:
            if content is not None:
                self._handle_content(content=content)
            if error is not None and isinstance(error, (str | list)):
                self._add_to_list(error, target_list=self.error)
            if isinstance(extra, dict):
                self._add_to_extra(value=extra)
            if log_output and self.logger and (content or error):
                self._log_handling(content=content, error=error, logger=self.logger)
        except Exception as e:
            raise ValueError(f"Failed to add content: {e!s}") from e
        return self.done(to_dict=True) if to_dict else self

    def _log_handling(
        self,
        content: str | list[str] | CompletedProcess[str] | FunctionResponse | None,
        error: str | list[str] | None,
        logger: Loggers,
    ) -> None:
        """Log the content and error messages if they exist."""
        content_msgs: list[str] = []
        error_msgs: list[str] = []

        if isinstance(content, (str | list)):
            content_msgs = [content] if isinstance(content, str) else content
            content_msgs = [msg for msg in content_msgs if msg]

        if isinstance(error, (str | list)):
            error_msgs = [error] if isinstance(error, str) else error
            error_msgs = [msg for msg in error_msgs if msg]

        if not content_msgs and not error_msgs:
            return

        if content_msgs and is_async(logger.info):
            con_task = create_async_task(log_task_async, output=content_msgs, log_func=logger.info)
            con_task.run()
        else:
            log_task(strings=content_msgs, log_func=logger.info)

        if error_msgs and is_async(logger.error):
            err_task = create_async_task(log_task_async, output=error_msgs, log_func=logger.error)
            err_task.run()
        else:
            log_task(strings=error_msgs, log_func=logger.error)

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Override model_dump to include dynamic attributes at the root level."""
        result: dict[str, Any] = super().model_dump(**kwargs)
        exclude: set = kwargs.get("exclude", set())
        dynamic: dict[str, Any] = self._dump_root()
        sub_tasks: dict[str, FunctionResponse] = dynamic.pop("sub_tasks", {})
        extra: dict[str, Any] = dynamic.pop("extra", {})
        if extra and "extra" not in exclude:
            result.update(dict(extra))
        if sub_tasks and "sub_tasks" not in exclude:
            result["sub_tasks"] = {}
            for name, task in sub_tasks.items():
                result["sub_tasks"][name] = task.model_dump(**kwargs)
        if dynamic and "dynamic" not in exclude:
            result.update(dynamic)
        return {k: v for k, v in result.items() if v not in (None, [], {}, "")}

    @overload
    def done(self, to_dict: LitTrue, suppress: list[str] | None = None) -> dict: ...
    @overload
    def done(self, to_dict: LitFalse, suppress: list[str] | None = None) -> Self: ...

    def done(self, to_dict: bool = False, suppress: list[str] | None = None) -> dict | Self:
        """Convert the FunctionResponse to a dictionary or return the instance itself.

        Args:
            to_dict (bool): If True, return a dictionary representation.
                If False, return the FunctionResponse instance.
            suppress (list[str] | None): List of keys to suppress in the output dictionary.

        Returns:
            dict[str, Any] | Self: The dictionary representation or the FunctionResponse instance for later use.
        """
        if not to_dict:
            return self

        exclude_set: set[str] = set(suppress or [])
        return self.model_dump(exclude=exclude_set, exclude_none=True)


if __name__ == "__main__":
    res = FunctionResponse(name="example_function")
    res.fart = "toot"
    res.add(content="This is a test content.", error="This is a test error.", extra={"key": "value"})
    res.sub_task(name="sub_task_1", content="Subtask content", error="Subtask error")
    print(res)
