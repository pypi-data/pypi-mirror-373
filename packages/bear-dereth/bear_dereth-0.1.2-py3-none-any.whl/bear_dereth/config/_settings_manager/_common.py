from collections.abc import Callable, Mapping
from hashlib import sha1
from pathlib import Path
from types import NoneType
from typing import Literal

from bear_dereth.config.dir_manager import get_settings_path

TypeList = Literal["string", "number", "float", "boolean", "null"]
"""A type alias for the allowed types in settings."""
ValueType = str | int | float | bool | NoneType
"""A type alias for the allowed value types in settings."""
PossibleTypes = type[bool] | type[int] | type[float] | type[str] | type[NoneType]
"""A type alias for the possible Python types corresponding to ValueType."""
QueryCheck = Callable[[Mapping], bool]
"""A type alias for a callable that checks a settings record."""
OpType = Literal["path", "==", "!=", ">", "<", ">=", "<=", "exists", "and", "or", "not", "matches", "all", "search"]
"""A type alias for the supported query operation types."""


def get_file_hash(path: Path) -> str:
    """Get a simple SHA1 hash of a file - fast and good enough for change detection.

    Args:
        path: Path to the file to hash

    Returns:
        str: Hex digest of the file contents, or empty string if file doesn't exist
    """
    if not path.exists() or not path.is_file():
        return ""

    try:
        return sha1(path.read_bytes(), usedforsecurity=False).hexdigest()
    except OSError:
        return ""  # File read error, treat as "no file"


def has_file_changed(path: Path, last_known_hash: str) -> tuple[bool, str]:
    """Function version - check if file changed and return new hash.

    Args:
        path: Path to check
        last_known_hash: Previous hash to compare against

    Returns:
        tuple[bool, str]: (has_changed, current_hash)
    """
    current_hash: str = get_file_hash(path)
    return (current_hash != last_known_hash, current_hash)


class FileWatcher:
    """Simple file change detection using SHA1 hashing."""

    def __init__(self, filepath: str | Path) -> None:
        """Initialize FileWatcher.

        Args:
            filepath: Path to the file to watch
        """
        self.path = Path(filepath)
        self._last_hash: str = get_file_hash(self.path)

    def has_changed(self) -> bool:
        """Check if file has changed since last check.

        Returns:
            bool: True if file changed, False otherwise
        """
        current_hash: str = get_file_hash(self.path)
        if current_hash != self._last_hash:
            self._last_hash = current_hash
            return True
        return False

    @property
    def current_hash(self) -> str:
        """Get current file hash without updating internal state."""
        return get_file_hash(self.path)


def get_path(name: str, file_name: str | None, path: Path | str | None = None) -> Path:
    """Get the path to the settings file.

    Args:
        name: App name (used as default file name and for default directory)
        file_name: Optional specific file name (overrides name for filename)
        path: Optional path - can be:
            - Full path to .json file (returns as-is)
            - Directory path (file will be created inside)
            - None (uses default settings directory)

    Returns:
        Path: Full path to the settings JSON file

    Examples:
        get_path("myapp")
        # -> ~/.config/myapp/settings/myapp.json

        get_path("myapp", "custom")
        # -> ~/.config/myapp/settings/custom.json

        get_path("myapp", None, "/tmp")
        # -> /tmp/myapp.json

        get_path("myapp", "custom", "/tmp")
        # -> /tmp/custom.json

        get_path("myapp", None, "/full/path/config.json")
        # -> /full/path/config.json
    """
    # FIXME: Do I need to do path sanitization here? I'm not sure of the threat here?
    if path is not None and str(path).endswith(".json"):
        path_obj: Path = Path(path).resolve()
        if path_obj.is_absolute() or "/" in str(path):
            return path_obj
    filename_base: str = name if file_name is None else Path(file_name).stem
    root_path: Path = Path(path) if path is not None else get_settings_path(name, mkdir=True)
    return root_path / f"{filename_base}.json"


class Document(dict):
    """A document stored in the database.

    This class provides a way to access both a document's content and
    its ID using ``doc.doc_id``.
    """

    def __init__(self, value: Mapping[str, ValueType], doc_id: int) -> NoneType:
        super().__init__(value)
        self.doc_id: int = doc_id
