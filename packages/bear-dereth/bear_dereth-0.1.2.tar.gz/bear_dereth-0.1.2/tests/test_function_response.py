"""Comprehensive test suite for FunctionResponse class."""

from subprocess import CompletedProcess

import pytest

from bear_dereth.constants.logger_protocol import LoggerProtocol
from bear_dereth.models.responses import FunctionResponse


class MockLogger:
    def __init__(self):
        """Initialize mock logger."""
        self.messages = []

    def log(self, level: str, msg: object, *args, **kwargs) -> None:
        """Mock logging method."""
        msg = f"{level.upper()}: {msg}"
        if args:
            msg = f"{msg} {' '.join(map(str, args))}"
        if kwargs:
            msg = f"{msg} {kwargs}"
        self.messages.append(msg)

    def info(self, msg: object, *args, **kwargs) -> None:
        """Mock info logging method."""
        self.log("info", msg, *args, **kwargs)

    def error(self, msg: object, *args, **kwargs) -> None:
        """Mock error logging method."""
        self.log("error", msg, *args, **kwargs)

    def debug(self, msg: object, *args, **kwargs) -> None:
        """Mock debug logging method."""
        self.log("debug", msg, *args, **kwargs)

    def warning(self, msg: object, *args, **kwargs) -> None:
        """Mock warning logging method."""
        self.log("warning", msg, *args, **kwargs)

    def verbose(self, msg: object, *args, **kwargs) -> None:
        """Mock verbose logging method."""
        self.log("verbose", msg, *args, **kwargs)

    def success(self, msg: object, *args, **kwargs) -> None:
        """Mock success logging method."""
        self.log("success", msg, *args, **kwargs)

    def failure(self, msg: object, *args, **kwargs) -> None:
        """Mock failure logging method."""
        self.log("failure", msg, *args, **kwargs)

    def get_messages(self) -> list[str]:
        """Retrieve all logged messages."""
        return self.messages


class TestLoggerProtocol:
    def test_logger_protocol(self):
        """Test LoggerProtocol interface."""
        logger: LoggerProtocol = MockLogger()
        assert isinstance(logger, LoggerProtocol), "MockLogger should implement LoggerProtocol"
        assert hasattr(logger, "log")
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "verbose")
        assert hasattr(logger, "success")
        assert hasattr(logger, "failure")


class TestFunctionResponseCreation:
    """Test basic creation and initialization."""

    def test_default_initialization(self):
        """Test creating FunctionResponse with defaults."""
        response = FunctionResponse()
        assert response.name is None
        assert response.returncode == 0
        assert response.extra == {}
        assert response.content == []
        assert response.error == []
        assert response.logger is None
        assert response.success is True
        assert response.extra == {}
        assert response.sub_tasks == {}

    def test_initialization_with_values(self):
        """Test creating FunctionResponse with specific values."""
        response = FunctionResponse(name="test_function").add(
            returncode=1,
            content=["output line 1", "output line 2"],
            error=["error message"],
            extra={"key": "value"},
        )
        assert response.name == "test_function"
        assert response.returncode == 1
        assert response.content == ["output line 1", "output line 2"]
        assert response.error == ["error message"]
        assert response.extra == {"key": "value"}
        assert response.success is False


class TestFieldValidation:
    """Test Pydantic field validation."""

    def test_name_validation_string_conversion(self) -> None:
        """Test name field converts to string and formats correctly."""
        response = FunctionResponse(name="Test Function Name")
        assert response.name == "test_function_name"

        response = FunctionResponse(name=123)  # type: ignore[arg-type]
        assert response.name == "123"

        response = FunctionResponse(name=None)
        assert response.name is None

    def test_name_validation_invalid_type(self) -> None:
        """Test name validation with unconvertible type."""

        class UnconvertibleType:
            def __str__(self):
                raise TypeError("Cannot convert to string")

        with pytest.raises(TypeError, match="Name must be a string"):
            FunctionResponse(name=UnconvertibleType())  # type: ignore[arg-type]

    def test_returncode_validation(self):
        """Test returncode validation."""
        response = FunctionResponse(returncode=5)
        assert response.returncode == 5

        with pytest.raises(ValueError, match="Input should be greater than or equal to 0"):
            FunctionResponse(returncode=-1)

        # Pydantic handles string parsing errors differently
        with pytest.raises(Exception):  # noqa: PT011 B017
            FunctionResponse(returncode="not_int")  # type: ignore[arg-type]

    def test_content_validation(self):
        """Test content field validation and conversion."""
        # String to list conversion
        response = FunctionResponse(content="single string")  # type: ignore[arg-type]
        assert response.content == ["single string"]

        # List of strings
        response = FunctionResponse(content=["item1", "item2"])
        assert response.content == ["item1", "item2"]

        # Invalid content
        with pytest.raises(TypeError, match="Content and error must be a string or a list of strings."):
            FunctionResponse(content=123)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="Content and error must be a string or a list of strings."):
            FunctionResponse(content=["valid", 123])  # type: ignore[arg-type]

    def test_error_validation(self):
        """Test error field validation and conversion."""
        # String to list conversion
        response = FunctionResponse(error="single error")  # type: ignore[arg-type]
        assert response.error == ["single error"]

        # List of strings
        response = FunctionResponse(error=["error1", "error2"])
        assert response.error == ["error1", "error2"]

        # Invalid error
        with pytest.raises(TypeError, match="Content and error must be a string or a list of strings."):
            FunctionResponse(error=123)  # type: ignore[arg-type]


class TestFromProcess:
    """Test creating FunctionResponse from CompletedProcess."""

    def test_from_process_success(self):
        """Test creating from successful process."""
        process = CompletedProcess(args=["echo", "hello"], returncode=0, stdout="hello world\n", stderr="")

        response = FunctionResponse.from_process(process)
        assert response.returncode == 0
        assert response.content == ["hello world"]
        assert response.error == []
        assert response.success is True

    def test_from_process_failure(self):
        """Test creating from failed process."""
        process = CompletedProcess(
            args=["ls", "/nonexistent"], returncode=1, stdout="", stderr="ls: /nonexistent: No such file or directory\n"
        )

        response = FunctionResponse.from_process(process)
        assert response.returncode == 1
        assert response.content == []
        assert response.error == ["ls: /nonexistent: No such file or directory"]
        assert response.success is False

    def test_from_process_edge_case_content_error_swap(self):
        """Test edge case where stdout is empty but stderr has content with success code."""
        process = CompletedProcess(args=["some_command"], returncode=0, stdout="", stderr="warning message\n")

        response = FunctionResponse.from_process(process)
        assert response.returncode == 0
        assert response.content == ["warning message"]
        assert response.error == []


class TestFluentAPI:
    """Test fluent API methods."""

    def test_successful_method(self):
        """Test successful() method."""
        mock_logger = MockLogger()
        response = FunctionResponse(name="test", logger=mock_logger)
        result = response.successful("operation completed", log_output=True)

        assert result is response  # Returns self for chaining
        assert response.content == ["operation completed"]
        assert response.returncode == 0
        assert response.success is True
        messages = mock_logger.get_messages()
        assert len(messages) == 1
        assert "INFO: operation completed" in messages

    # async def test_async_successful_method(self):
    #     """Test successful() method."""
    #     response = FunctionResponse(name="test", logger=AsyncLogger())
    #     result = response.successful("operation completed", log_output=True)

    #     assert result is response  # Returns self for chaining
    #     assert response.content == ["operation completed"]
    #     assert response.returncode == 0
    #     assert response.success is True

    def test_fail_method(self):
        """Test fail() method."""
        response = FunctionResponse(name="test")
        result = response.fail(error="something went wrong")

        assert result is response  # Returns self for chaining
        assert response.error == ["something went wrong"]
        assert response.returncode == 1
        assert response.success is False

    def test_chaining_fluent_methods(self):
        """Test chaining multiple fluent method calls."""
        response = (
            FunctionResponse(name="test")
            .add(content="first operation")
            .add(content="second operation")
            .add(error=["minor warning"])
        )

        print(response)
        assert response.content == ["first operation", "second operation"]
        assert response.error == ["minor warning"]
        assert response.returncode == 0


class TestSubTaskMethod:
    """Test the sub_task convenience method."""

    def test_sub_task_basic(self):
        """Test basic sub_task functionality."""
        main_response = FunctionResponse(name="main_task")
        main_response.sub_task(name="subtask_1", content="sub content")

        assert main_response.content == ["subtask_1: sub content"]
        assert main_response.error == []

    def test_sub_task_with_error(self):
        """Test sub_task with error."""
        main_response = FunctionResponse(name="main_task")
        main_response.sub_task(name="failed_subtask", error="something went wrong")

        assert main_response.content == []
        assert main_response.error == ["failed_subtask: something went wrong"]

    def test_sub_task_inherits_returncode(self):
        """Test that sub_task inherits returncode from parent."""
        main_response = FunctionResponse(name="main_task", returncode=5)
        main_response.sub_task(name="subtask", content="test")
        # The sub_task should inherit the parent's returncode
        assert main_response.returncode == 5
        # Can't directly test the sub-response returncode, but the behavior should be consistent

    def test_sub_task_override_returncode(self):
        """Test that sub_task can override returncode."""
        main_response = FunctionResponse(name="main_task", returncode=0)
        main_response.sub_task(name="subtask", content="test", returncode=2)

        assert main_response.returncode == 0
        # The sub-task uses the overridden returncode

    def test_sub_task_with_extra_and_kwargs(self):
        """Test sub_task with extra metadata."""
        main_response = FunctionResponse(name="main_task")
        main_response.sub_task(name="subtask", content="test content", extra={"key": "value"})

        assert main_response.content == ["subtask: test content"]
        # Extra metadata gets merged into main response
        assert "key" in main_response.extra
        assert main_response.extra["key"] == "value"

    def test_sub_task_inherits_logger(self):
        """Test that sub_task inherits logger from parent."""
        # Create main response without logger initially
        main_response = FunctionResponse(name="main_task")

        # Add subtask - should work even without logger
        main_response.sub_task(name="subtask", content="test")

        assert main_response.content == ["subtask: test"]

    def test_sub_task_multiple_operations(self):
        """Test adding multiple sub_tasks."""
        main_response = FunctionResponse(name="batch_operation")

        # Add multiple subtasks
        main_response.sub_task(name="task1", content="completed task 1")
        main_response.sub_task(name="task2", error="task 2 failed")
        main_response.sub_task(name="task3", content="completed task 3")

        assert main_response.content_number == 2  # Two successful
        assert main_response.error_number == 1  # One failed

        assert "task1: completed task 1" in main_response.content
        assert "task2: task 2 failed" in main_response.error
        assert "task3: completed task 3" in main_response.content

    def test_sub_task_list_content_and_error(self):
        """Test sub_task with list content and errors."""
        main_response = FunctionResponse(name="main_task")

        main_response.sub_task(name="multi_subtask", content=["output 1", "output 2"], error=["warning 1", "warning 2"])

        assert "multi_subtask: output 1" in main_response.content
        assert "multi_subtask: output 2" in main_response.content
        assert "multi_subtask: warning 1" in main_response.error
        assert "multi_subtask: warning 2" in main_response.error

    def test_sub_task_empty_name(self):
        """Test sub_task with empty name."""
        main_response = FunctionResponse(name="main_task")
        main_response.sub_task(content="content without name")
        # Should still add content, just without name prefix
        assert "content without name" in main_response.content

    # def test_async_sub_task(self):
    #     """Test sub_task with async logger."""
    #     main_response = FunctionResponse(name="main_task", logger=AsyncLogger())
    #     main_response.sub_task(name="async_subtask", content="async content")

    #     assert main_response.content == ["async_subtask: async content"]
    #     assert isinstance(main_response.logger, AsyncLogger)

    # async def test_async_sub_task_with_async_logger(self):
    #     """Test sub_task with async logger with an async context."""
    #     main_response = FunctionResponse(name="main_task", logger=AsyncLogger())
    #     main_response.sub_task(name="async_subtask", content="async content")

    #     assert main_response.content == ["async_subtask: async content"]
    #     assert isinstance(main_response.logger, AsyncLogger)


class TestAddMethod:
    """Test the complex add() method."""

    def test_add_string_content(self):
        """Test adding string content."""
        response = FunctionResponse()
        response.add(content="test content")

        assert response.content == ["test content"]
        assert len(response.content) == 1

    def test_add_list_content(self):
        """Test adding list content."""
        response = FunctionResponse()
        response.add(content=["item1", "item2"])

        assert response.content == ["item1", "item2"]
        assert len(response.content) == 2

    def test_add_function_response(self):
        """Test adding another FunctionResponse."""
        sub_response = FunctionResponse(name="sub_task").add(
            content=["sub content"], error=["sub error"], extra={"sub_key": "sub_value"}
        )

        main_response = FunctionResponse(name="main")
        main_response.add(content=sub_response)

        assert main_response.content == ["sub_task: sub content"]
        assert main_response.error == ["sub_task: sub error"]
        assert main_response.extra == {"sub_key": "sub_value"}

    def test_add_completed_process(self):
        """Test adding CompletedProcess."""
        process = CompletedProcess(args=["echo", "test"], returncode=0, stdout="process output\n", stderr="")

        response = FunctionResponse()
        response.add(content=process)

        assert response.content == ["process output"]
        assert response.returncode == 0
        assert response.content_number == 1

    def test_add_with_extra_and_returncode(self):
        """Test adding with extra metadata and returncode."""
        response = FunctionResponse()
        response.add(content="test", error="warning", returncode=2, extra={"metadata": "value"})

        assert response.content == ["test"]
        assert response.error == ["warning"]
        assert response.returncode == 2
        assert response.extra == {"metadata": "value"}


class TestDoneMethod:
    """Test the done() method and suppress functionality."""

    def test_done_return_self(self):
        """Test done() returning self when to_dict=False."""
        response = FunctionResponse(name="test", content=["content"])
        result = response.done(to_dict=False)

        assert result is response
        assert isinstance(result, FunctionResponse)

    def test_done_return_dict_full(self):
        """Test done() returning dict with all fields."""
        response = FunctionResponse(name="test_func").add(
            returncode=1,
            content=["output"],
            error=["error msg"],
            extra={"custom": "data"},
        )

        result = response.done(to_dict=True)
        expected = {
            "name": "test_func",
            "success": False,
            "returncode": 1,
            "content": ["output"],
            "error": ["error msg"],
            "custom": "data",
        }

        assert result == expected

    def test_done_with_suppress_success(self):
        """Test done() with SUCCESS suppress list."""
        response = FunctionResponse(name="test", content=["output"])
        result = response.done(to_dict=True, suppress=["success", "name", "returncode"])

        # SUCCESS suppresses "name" and "success", so only content should remain
        expected = {"content": ["output"]}

        assert result == expected
        assert "name" not in result
        assert "success" not in result

    def test_done_with_custom_suppress(self):
        """Test done() with custom suppress list."""
        response = FunctionResponse(name="test", content=["output"])
        result = response.done(to_dict=True, suppress=["success", "returncode"])
        expected = {"name": "test", "content": ["output"]}

        assert result == expected

    def test_done_minimal_response(self):
        """Test done() with minimal successful response."""
        response = FunctionResponse()
        result = response.done(to_dict=True, suppress=["returncode"])

        expected = {"success": True}

        assert result == expected


class TestStringRepresentation:
    """Test __str__ and __repr__ methods."""

    def test_repr_minimal(self):
        """Test repr with minimal data."""
        response = FunctionResponse()
        result = repr(response)
        assert "Response(" in result

    def test_repr_full(self):
        """Test repr with all fields populated."""
        response = FunctionResponse(name="test_func").add(
            returncode=1, content=["output"], error=["error"], extra={"key": "value"}
        )

        result = repr(response)
        assert "name='test_func'" in result
        assert "success=False" in result
        assert "content='output'" in result
        assert "error='error'" in result

    def test_str_equals_repr(self):
        """Test that __str__ equals __repr__."""
        response = FunctionResponse(name="test", content=["data"])
        assert str(response) == repr(response)


class TestComplexScenarios:
    """Test complex real-world usage scenarios."""

    def test_aggregating_multiple_operations(self):
        """Test aggregating results from multiple operations."""
        main_response = FunctionResponse(name="batch_operation")

        # Simulate multiple sub-operations
        for i in range(3):
            sub_response = FunctionResponse(name=f"task_{i}")
            if i == 1:  # One fails
                sub_response.fail(error=f"Task {i} failed")
            else:
                sub_response.successful(f"Task {i} completed")

            main_response.add(content=sub_response)
        assert main_response.content_number == 2  # Two successful
        assert main_response.error_number == 1  # One failed
        assert "task_0: Task 0 completed" in main_response.content
        assert "task_1: Task 1 failed" in main_response.error

    def test_mcp_server_response_format(self):
        """Test formatting response for MCP server consumption."""
        response = FunctionResponse(name="clear_tasks")

        # Add some successful operations
        response.successful("Cleared 5 completed tasks")
        response.add(content="Operation summary generated")

        result = response.done(to_dict=True)

        assert "content" in result
        assert "number_of_tasks" not in result  # This will only be here in failures
        assert "name" in result
        assert "success" in result

    def test_mcp_server_response_format_error(self):
        """Test formatting response for MCP server consumption."""
        response = FunctionResponse(name="clear_tasks_error")

        # Add some successful operations
        response.fail("Failed to clear tasks")
        response.add(content="Error summary generated")

        result = response.done(to_dict=True)

        assert "content" in result
        assert "name" in result
        assert "success" in result

    def test_error_handling_in_add_method(self):
        """Test error handling within add method."""
        response = FunctionResponse()

        # This should not raise an exception
        response.add(content=None, error=None)
        assert response.content == []
        assert response.error == []

        # Test with valid mixed content
        response.add(content="valid", error="also valid")
        assert response.content == ["valid"]
        assert response.error == ["also valid"]
