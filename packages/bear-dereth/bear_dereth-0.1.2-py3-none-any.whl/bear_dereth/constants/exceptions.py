"""Custom exceptions for the application."""

from types import NoneType


class ObjectTypeError(TypeError):
    """Base class for object type errors."""

    def __init__(self, expected: type = NoneType, received: type = NoneType, **kwargs) -> None:
        """Initialize the ObjectTypeError with expected and received types."""
        if kwargs.get("msg") is not None:
            super().__init__(kwargs.pop("msg"))
            return
        super().__init__(f"Expected object of type {expected.__name__}, but got {received.__name__}.")


class InputObjectError(ObjectTypeError):
    """Exception raised for errors in the input object type."""

    def __init__(self, expected: type, received: type) -> None:
        """Initialize the InputObjectError with expected and received types."""
        msg: str = f"Expected input object of type {expected.__name__}, but got {received.__name__}."
        super().__init__(msg=msg)


class OutputObjectError(ObjectTypeError):
    """Exception raised for errors in the output object type."""

    def __init__(self, expected: type, received: type) -> None:
        """Initialize the OutputObjectError with expected and received types."""
        msg: str = f"Expected output object of type {expected.__name__}, but got {received.__name__}."
        super().__init__(msg=msg)


class UserCancelledError(Exception):
    """Exception raised when a user cancels an operation."""

    def __init__(self, message: str = "User cancelled the operation") -> None:
        """Initialize the UserCancelledError with an optional message."""
        super().__init__(message)


class UnexpectedStatusCodeError(Exception):
    """Exception raised for unexpected HTTP status codes."""

    def __init__(self, status_code: int, message: str = "Unexpected status code received") -> None:
        """Initialize the UnexpectedStatusCodeError with status code and message."""
        super().__init__(f"{message}: {status_code}")


class HandlerNotFoundError(Exception):
    """Exception raised when an event handler is not found."""

    def __init__(self, event_name: str) -> None:
        """A handler was not found for the given event name."""
        super().__init__(f"No handler found for event: {event_name}")


class StateTransitionError(Exception):
    """Custom exception for state transition errors."""
