"""A module for detecting the current operating system."""

from contextlib import suppress
from enum import StrEnum
import platform
from typing import Any

from pydantic import BaseModel, Field


class OS(StrEnum):
    """Enumeration of operating systems."""

    DARWIN = "Darwin"
    """MacOS platform also known as Darwin."""
    LINUX = "Linux"
    """Linux platform."""
    WINDOWS = "Windows"
    """Windows platform."""
    BSD = "BSD"
    """BSD platform."""
    OTHER = "Other"
    """Other or unsupported platform."""


def get_platform() -> OS:
    """Return the current operating system as an :class:`OS` enum.

    Returns:
        OS: The current operating system as an enum member, or `OS.OTHER` if the platform is not recognized.
    """
    system: str = platform.system()
    return OS(system) if system in OS.__members__.values() else OS.OTHER


def is_macos() -> bool:
    """Return ``True`` if running on macOS."""
    return get_platform() == OS.DARWIN


def is_windows() -> bool:
    """Return ``True`` if running on Windows."""
    return get_platform() == OS.WINDOWS


def is_linux() -> bool:
    """Return ``True`` if running on Linux."""
    return get_platform() == OS.LINUX


class OSInfo(BaseModel):
    """Operating system information."""

    os: str = Field(default="", description="Detected OS name.")
    detected_os: OS = Field(default_factory=get_platform, description="Detected OS enum value.")
    version: str = Field(default="", description="Detected OS version.")

    def model_post_init(self, context: Any) -> None:
        """Post-initialization to information."""
        match self.detected_os:
            case OS.DARWIN:
                self.os = "macOS"
                try:
                    self.version = platform.mac_ver()[0]
                except Exception:
                    self.version = platform.release()
            case OS.LINUX:
                self.os = "Linux"
                self.version = linux_helper()
            case OS.BSD:
                self.os = "BSD"
                self.version = platform.release()
            case OS.WINDOWS:
                self.os = "Windows"
                try:
                    self.version = platform.win32_ver()[0]
                except Exception:
                    self.version = platform.release()
            case _:
                self.os = "Unknown"
                self.version = platform.platform(aliased=True, terse=True)
        return super().model_post_init(context)


def linux_helper() -> str:
    """Helper to get a pretty Linux version string."""
    _pretty = None
    with suppress(ImportError):
        import distro as _d  # noqa: PLC0415

        _pretty = _d.name(pretty=True) or " ".join(x for x in (_d.id(), _d.version()) if x)
    if _pretty:
        return _pretty
    with suppress(Exception):
        info: dict[str, str] = platform.freedesktop_os_release()
        return info.get("PRETTY_NAME", "")
    return platform.release()


def get_os_info(detected: OS | None = None) -> OSInfo:
    """Helper so callers/tests can inject an OS, otherwise auto-detect."""
    return OSInfo(detected_os=detected or get_platform())


DARWIN = OS.DARWIN
LINUX = OS.LINUX
WINDOWS = OS.WINDOWS
BSD = OS.BSD
OTHER = OS.OTHER


__all__ = [
    "DARWIN",
    "LINUX",
    "OS",
    "OTHER",
    "WINDOWS",
    "OSInfo",
    "get_os_info",
    "get_platform",
    "is_linux",
    "is_macos",
    "is_windows",
    "linux_helper",
]
