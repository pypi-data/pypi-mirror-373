"""A simple counter class that can be used to track state transitions."""

from itertools import count as counter
from typing import Annotated, Any, Self

from pydantic import BaseModel, Field


class Counter(BaseModel):
    """A simple counter class that can be used to track state transitions."""

    start: Annotated[int, Field(default=0, ge=0)] = 0
    count: Annotated[int, Field(default=0, ge=0, exclude=None)] = 0

    counter_: counter[int] = Field(default_factory=lambda: counter(0), exclude=True)

    model_config = {"arbitrary_types_allowed": True}

    def model_post_init(self, context: Any) -> None:
        """Initialize the counter after the model is created."""
        self._set(self.start)
        return super().model_post_init(context)

    def reset(self, value: int = 0) -> None:
        """Reset the counter to a specific value, defaults to 0."""
        self._set(value)

    def get(self, before: bool = False, after: bool = False) -> int:
        """Get the current value of the counter.

        Args:
            before (bool): If True, increment the counter before getting the value.
            after (bool): If True, increment the counter after getting the value.
        """
        if before:
            self.tick()
            return self.count
        if after:
            current_value: int = self.count
            self.tick()
            return current_value
        return self.count

    def set(self, value: int) -> Self:
        """Set the counter to a specific value.

        Args:
            value (int): The value to set the counter to. Must be non-negative and not
                            less than the current counter value.
        """
        if value < 0:
            raise ValueError("Counter value cannot be negative.")
        if value < self.count:
            raise ValueError("Cannot set counter to a value less than the current counter value.")
        self._set(value)
        return self

    def tick(self) -> int:
        """Increment the counter and return the new value."""
        self.count = next(self.counter_)
        return self.count

    def _set(self, value: int) -> None:
        """Set the counter to a specific value without validation."""
        self.counter_ = counter(value)
        self.count: int = next(self.counter_)

    def __repr__(self) -> str:
        """Return a string representation of the counter."""
        return f"Counter(start={self.start}, count={self.count})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another integer."""
        return self.count == other

    def __lt__(self, other: int) -> bool:
        """Check if the counter is less than another integer."""
        return self.count < other

    def __le__(self, other: int) -> bool:
        """Check if the counter is less than or equal to another integer."""
        return self.count <= other

    def __gt__(self, other: int) -> bool:
        """Check if the counter is greater than another integer."""
        return self.count > other

    def __ge__(self, other: int) -> bool:
        """Check if the counter is greater than or equal to another integer."""
        return self.count >= other

    def __hash__(self) -> int:
        """Return the hash of the current counter value."""
        return hash(self.count)

    def __int__(self) -> int:
        """Return the current counter value as an integer."""
        return self.count

    def __next__(self) -> int:
        """Return the next counter value."""
        return self.tick()
