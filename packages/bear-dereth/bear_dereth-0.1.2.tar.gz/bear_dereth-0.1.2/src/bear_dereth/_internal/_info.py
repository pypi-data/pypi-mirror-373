from contextlib import suppress
from importlib.metadata import PackageNotFoundError, distribution, version
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator
from pydantic.dataclasses import dataclass

from bear_dereth._internal._version import __commit_id__, __version__, __version_tuple__


@dataclass
class _Package:
    """Dataclass to store package information."""

    name: str
    """Package name."""
    version: str = "0.0.0"
    """Package version."""
    description: str = "No description available."
    """Package description."""

    def __str__(self) -> str:
        """String representation of the package information."""
        return f"{self.name} v{self.version}: {self.description}"


def _get_package_info(dist: str) -> _Package:
    """Get package information for the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        Package information with version, name, and description.
    """
    return _Package(name=dist, version=_get_version(dist), description=_get_description(dist))


def _get_version(dist: str = "bear-dereth") -> str:
    """Get version of the given distribution or the current package.

    Parameters:
        dist: A distribution name.

    Returns:
        A version number.
    """
    try:
        return version(dist)
    except PackageNotFoundError:
        return "0.0.0"


def _get_description(dist: str = "bear-dereth") -> str:
    """Get description of the given distribution or the current package.

    Parameters:
        dist: A distribution name.

    Returns:
        A description string.
    """
    try:
        return distribution(dist).metadata.get("summary", "No description available.")
    except PackageNotFoundError:
        return "No description available."


class _ProjectName(BaseModel):
    """A class to represent the project name and its metadata as literals for type safety.

    This is done this way to make it easier to see the values in the IDE and to ensure that the values are consistent throughout the codebase.
    """

    @property
    def package_distribution(self) -> Literal["bear-dereth"]:
        """Get the package distribution name."""
        return "bear-dereth"

    @property
    def project(self) -> Literal["bear_dereth"]:
        """Get the project name in lowercase with underscores."""
        return "bear_dereth"

    @property
    def project_upper(self) -> Literal["BEAR_DERETH"]:
        """Get the project name in uppercase with underscores."""
        return "BEAR_DERETH"

    @property
    def env_variable(self) -> Literal["BEAR_DERETH_ENV"]:
        """Get the environment variable name for the project."""
        return "BEAR_DERETH_ENV"


class _ProjectVersion(BaseModel):
    """A class to represent the project version."""

    string: str = Field(default=..., description="Project version.")
    tuple_: tuple[int, int, int] = Field(default=..., description="Project version as a tuple.")
    commit_id: str = Field(default=__commit_id__, description="Commit ID of the current version.")

    @field_validator("string", mode="before")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate the version string."""
        if not isinstance(v, str) or "0.0.0" in v:
            with suppress(PackageNotFoundError):
                return _get_version("bear-dereth")
            return "0.0.0"
        return v

    @field_validator("tuple_", mode="before")
    @classmethod
    def validate_version_tuple(cls, v: Any) -> tuple[int, int, int]:
        """Validate the version tuple."""
        parts = 3
        if not isinstance(v, tuple) or v == (0, 0, 0):
            with suppress(Exception):
                value: str = _get_version("bear-dereth")
                v = tuple(int(x) for x in value.split(".") if x.isdigit())
                if len(v) == parts:
                    return v
            return (0, 0, 0)
        return v


class _ProjectMetadata(BaseModel):
    """Dataclass to store the current project metadata."""

    version_: _ProjectVersion = Field(default=..., description="Project version information.")
    name_: _ProjectName = _ProjectName()

    def __str__(self) -> str:
        """String representation of the project metadata."""
        return f"{self.full_version}: {self.description}"

    @property
    def version(self) -> str:
        """Get the project version as a string."""
        return self.version_.string

    @property
    def version_tuple(self) -> tuple[int, int, int]:
        """Get the project version as a tuple."""
        return self.version_.tuple_

    @property
    def commit_id(self) -> str:
        """Get the Git commit ID of the current version."""
        return self.version_.commit_id

    @property
    def full_version(self) -> str:
        """Get the full version string."""
        return f"{self.name} v{self.version_.string}"

    @property
    def description(self) -> str:
        """Get the project description from the distribution metadata."""
        return _get_description(self.name)

    @property
    def name(self) -> Literal["bear-dereth"]:
        """Get the package distribution name."""
        return self.name_.package_distribution

    @property
    def name_upper(self) -> Literal["BEAR_DERETH"]:
        """Get the project name in uppercase with underscores."""
        return self.name_.project_upper

    @property
    def project_name(self) -> Literal["bear_dereth"]:
        """Get the project name."""
        return self.name_.project

    @property
    def env_variable(self) -> Literal["BEAR_DERETH_ENV"]:
        """Get the environment variable name for the project.

        Used to check if the project is running in a specific environment.
        """
        return self.name_.env_variable


_METADATA = _ProjectMetadata(
    version_=_ProjectVersion(
        string=__version__ if __version__ != "0.0.0" else _get_version("bear-dereth"),
        commit_id=__commit_id__,
        tuple_=__version_tuple__,
    )
)


__all__ = ["_METADATA"]
