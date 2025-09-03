"""A module defining common exit codes used in shell commands."""

from bear_dereth.tools.rich_enums import IntValue as Value, RichIntEnum


class ExitCode(RichIntEnum):
    """An enumeration of common exit codes used in shell commands."""

    SUCCESS = Value(0, "Success")
    """An exit code indicating success."""
    FAILURE = Value(1, "General error")
    """An exit code indicating a general error."""
    MISUSE_OF_SHELL_COMMAND = Value(2, "Misuse of shell command")
    """An exit code indicating misuse of a shell command."""
    COMMAND_CANNOT_EXECUTE = Value(126, "Command invoked cannot execute")
    """An exit code indicating that the command invoked cannot execute."""
    COMMAND_NOT_FOUND = Value(127, "Command not found")
    """An exit code indicating that the command was not found."""
    INVALID_ARGUMENT_TO_EXIT = Value(128, "Invalid argument to exit")
    """An exit code indicating an invalid argument to exit."""
    SCRIPT_TERMINATED_BY_CONTROL_C = Value(130, "Script terminated by Control-C")
    """An exit code indicating that the script was terminated by Control-C."""
    PROCESS_KILLED_BY_SIGKILL = Value(137, "Process killed by SIGKILL (9)")
    """An exit code indicating that the process was killed by SIGKILL (9)."""
    SEGMENTATION_FAULT = Value(139, "Segmentation fault (core dumped)")
    """An exit code indicating a segmentation fault (core dumped)."""
    PROCESS_TERMINATED_BY_SIGTERM = Value(143, "Process terminated by SIGTERM (15)")
    """An exit code indicating that the process was terminated by SIGTERM (15)."""
    EXIT_STATUS_OUT_OF_RANGE = Value(255, "Exit status out of range")
    """An exit code indicating that the exit status is out of range."""
