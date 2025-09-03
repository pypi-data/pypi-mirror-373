"""Common file extensions and paths used in the application."""

from os import environ
from pathlib import Path


def get_config_path() -> Path:
    """Get the path to the configuration directory based on the operating system."""
    if "XDG_CONFIG_HOME" in environ:
        return Path(environ["XDG_CONFIG_HOME"])
    if "APPDATA" in environ:
        return Path(environ["APPDATA"])
    return Path.home() / ".config"


PATH_TO_DOWNLOADS: Path = Path.home() / "Downloads"
"""Path to the Downloads folder."""
PATH_TO_PICTURES: Path = Path.home() / "Pictures"
"""Path to the Pictures folder."""
PATH_TO_DOCUMENTS: Path = Path.home() / "Documents"
"""Path to the Documents folder."""
PATH_TO_CONFIG: Path = Path.home() / ".config"
"""Path to the .config folder."""
PATH_TO_HOME: Path = Path.home()
"""Path to the user's home directory."""
PATH_TO_CONFIG: Path = get_config_path()
"""Path to the configuration directory based on the operating system."""
