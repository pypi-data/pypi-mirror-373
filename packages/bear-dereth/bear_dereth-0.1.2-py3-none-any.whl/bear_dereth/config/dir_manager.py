"""Directory Manager Module for Bear Utils."""

from pathlib import Path
import shutil
import tempfile
from typing import ClassVar

from bear_dereth.constants.common_paths import (
    PATH_TO_CONFIG,
    PATH_TO_DOCUMENTS,
    PATH_TO_DOWNLOADS,
    PATH_TO_HOME,
    PATH_TO_PICTURES,
)


class DirectoryManager:
    """A class to manage application directories."""

    _base_path: ClassVar[Path] = PATH_TO_CONFIG

    def __init__(self, name: str) -> None:
        """Initialize the DirectoryManager with a specific name."""
        self.name: str = name
        self.home: Path = PATH_TO_HOME
        self.cwd: Path = Path.cwd()
        self.downloads: Path = PATH_TO_DOWNLOADS
        self.pictures: Path = PATH_TO_PICTURES
        self.documents: Path = PATH_TO_DOCUMENTS
        self._config: Path = self._base_path / self.name
        self._local_config: Path = self.cwd / "config" / self.name
        self._settings: Path = self._config / "settings"
        self._cache: Path = self.home / ".cache" / self.name
        self.custom_dirs: dict[str, Path] = {}

    def register(self, name: str, path: Path, mkdir: bool = False) -> None:
        """Register a custom directory path.

        Args:
            name: The name to register the path under.
            path: The custom path to register.
            mkdir: Whether to create the directory if it doesn't exist.
        """
        if mkdir and not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        self.custom_dirs[name] = path

    def __getattr__(self, item: str) -> Path:
        """Get a registered custom directory path."""
        if item in self.custom_dirs:
            return self.custom_dirs[item]
        raise AttributeError(f"'DirectoryManager' object has no attribute '{item}'")

    def __getitem__(self, item: str) -> Path:
        """Get a registered custom directory path using item access."""
        return self.__getattr__(item)

    def config(self, mkdir: bool = False) -> Path:
        """Get the path to the base configuration directory.

        ~/.config/<name>
        """
        if mkdir and not self._config.exists():
            self._config.mkdir(parents=True, exist_ok=True)
        return self._config

    def local_config(self, mkdir: bool = False) -> Path:
        """Get the path to the local configuration directory.

        <Path.cwd()>/config/<name>
        """
        if mkdir and not self._local_config.exists():
            self._local_config.mkdir(parents=True, exist_ok=True)
        return self._local_config

    def settings(self, mkdir: bool = False) -> Path:
        """Get the path to the settings directory.

        ~/.config/<name>/settings
        """
        if mkdir and not self._settings.exists():
            self._settings.mkdir(parents=True, exist_ok=True)
        return self._settings

    def temp_path(self, mkdir: bool = False) -> Path:
        """Get the path to the temporary directory."""
        if not self.name:
            raise ValueError("Name must be set to get the temporary path.")
        temp_path: Path = Path(tempfile.gettempdir()) / self.name
        if mkdir and not temp_path.exists():
            temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path

    def clear_temp(self) -> None:
        """Clear the temporary directory."""
        path: Path = self.temp_path()
        if path.exists():
            shutil.rmtree(path)

    def cache_path(self, mkdir: bool = False) -> Path:
        """Get the path to the cache directory.

        ~/.cache/<name>
        """
        path: Path = Path.home() / ".cache" / self.name
        if mkdir and not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path


def get_config_path(name: str, mkdir: bool = False) -> Path:
    """Get the base path for the user at an arbitrary config directory."""
    return DirectoryManager(name).config(mkdir)


def get_local_config_path(name: str, mkdir: bool = False) -> Path:
    """Get the local config path for the local config directory, usually config/."""
    return DirectoryManager(name).local_config(mkdir)


def get_settings_path(name: str, mkdir: bool = False) -> Path:
    """Get the path to the settings directory."""
    return DirectoryManager(name).settings(mkdir)


def get_temp_path(name: str, mkdir: bool = False) -> Path:
    """Get the path to the temporary directory."""
    return DirectoryManager(name).temp_path(mkdir)


def get_cache_path(name: str, mkdir: bool = False) -> Path:
    """Get the path to the cache directory."""
    return DirectoryManager(name).cache_path(mkdir)


def clear_temp_directory(name: str) -> None:
    """Clear the temporary directory."""
    DirectoryManager(name).clear_temp()


__all__ = [
    "DirectoryManager",
    "clear_temp_directory",
    "get_cache_path",
    "get_config_path",
    "get_local_config_path",
    "get_settings_path",
    "get_temp_path",
]
