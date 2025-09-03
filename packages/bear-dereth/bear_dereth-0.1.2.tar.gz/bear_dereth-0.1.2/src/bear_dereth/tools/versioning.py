"""Module for versioning functionality, including getting and bumping package versions."""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from contextlib import redirect_stdout
from importlib.metadata import PackageNotFoundError, version
from io import StringIO
import re
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, Field

from bear_dereth.constants.enums import VALID_BUMP_TYPES, ExitCode, VersionParts
from bear_dereth.tools.cli.arg_helpers import CLIArgsType, args_parse

BumpType = Literal["major", "minor", "patch"]

PositiveInt = Annotated[int, Field(ge=0, lt=1000)]


class Parts[*P](tuple):
    """A list subclass to represent version parts."""

    THREE_PARTS = 3
    FOUR_PARTS = 4

    @classmethod
    def split(cls, s: str, sep: str = ".") -> Parts[Any]:
        """A quick split method."""
        return Parts[int | str]([part for part in s.split(sep) if part][:4])

    @property
    def three(self) -> bool:
        """Check if the version has three parts."""
        return len(self) == self.THREE_PARTS

    @property
    def four(self) -> bool:
        """Check if the version has four parts."""
        return len(self) == self.FOUR_PARTS

    def to_three(self) -> Parts[int, int, int]:
        """Assert this is has three parts."""
        if self.three and self.is_valid:
            return Parts[int, int, int](self)
        raise ValueError("Has less or more than three parts.")

    def to_four(self) -> Parts[int, int, int, str]:
        """Assert this is has three parts."""
        if self.four and self.is_valid:
            return Parts[int, int, int, str](self)
        raise ValueError(f"Has less or more than four parts: {self}")

    def check_three_parts(self) -> bool:
        """Check that the first three parts are integers."""
        return len(self) >= self.THREE_PARTS and all(isinstance(int(part), int) for part in self[:3])

    def check_forth_part(self) -> bool:
        """Check that 4th part is a str."""
        return self.four and isinstance(str(self[3]), str)

    @property
    def is_valid(self) -> bool:
        """Check if the version parts are valid."""
        if self.three:
            return self.check_three_parts()
        if self.four:
            return self.check_three_parts() and self.check_forth_part()
        return False


class Version(BaseModel):
    """Model to represent a version string."""

    major: PositiveInt = 0
    """Major version number."""
    minor: PositiveInt = 0
    """Minor version number."""
    patch: PositiveInt = 0
    """Patch version number."""
    post: str | None = Field(default=None)
    """Post-release identifier."""

    def __repr__(self) -> str:
        """Return a string representation of the Version instance."""
        return (
            f"{self.major}.{self.minor}.{self.patch}.{self.post}"
            if self.post
            else f"{self.major}.{self.minor}.{self.patch}"
        )

    def __str__(self) -> str:
        """Return a string representation of the Version instance."""
        return self.__repr__()

    @classmethod
    def _from_parts(cls, parts: Parts[Any]) -> Self:
        """Create a Version instance from individual parts."""
        if parts.three:
            int_parts: Parts[int, int, int] = parts.to_three()
            return cls(major=int_parts[0], minor=int_parts[1], patch=int_parts[2])
        if parts.four:
            full_parts: Parts[int, int, int, str] = parts.to_four()
            return cls(major=full_parts[0], minor=full_parts[1], patch=full_parts[2], post=full_parts[3])
        raise ValueError(f"Invalid number of parts. Expected 3 or 4 parts: {parts}")

    @classmethod
    def from_string(cls, version_str: str) -> Self:
        """Create a Version instance from a version string.

        Args:
            version_str: A version string in the format "major.minor.patch".

        Returns:
            A Version instance.

        Raises:
            ValueError: If the version string is not in the correct format.
        """
        if "-" in version_str:
            version_str = version_str.split("-")[0]
        if "+" in version_str:
            version_str = version_str.split("+")[0]
        version_str = re.sub(r"^[vV]", "", version_str)
        return cls._from_parts(Parts.split(version_str, "."))

    def increment(self, attr_name: str) -> None:
        """Increment the specified part of the version."""
        setattr(self, attr_name, getattr(self, attr_name) + 1)

    def default(self, part: str) -> None:
        """Clear the specified part of the version.

        Args:
            part: The part of the version to clear.
        """
        if hasattr(self, part):
            setattr(self, part, 0)

    def new_version(self, bump_type: str) -> Version:
        """Return a new version string based on the bump type."""
        bump_part: VersionParts = VersionParts.get(bump_type, default=VersionParts.PATCH)
        self.increment(bump_part.text)
        for part in VersionParts:
            if part.value > bump_part.value:
                self.default(part.text)
        return self

    @classmethod
    def from_meta(cls, package_name: str) -> Self:
        """Create a Version instance from the current package version.

        Returns:
            A Version instance with the current package version.

        Raises:
            PackageNotFoundError: If the package is not found.
        """
        try:
            return cls.from_string(version(package_name))
        except PackageNotFoundError as e:
            raise PackageNotFoundError(f"Package '{package_name}' not found: {e}") from e


def _bump_version(version: str, bump_type: Literal["major", "minor", "patch"]) -> Version:
    """Bump the version based on the specified type, mutating in place since there is no reason not to.

    Args:
        version: The current version string (e.g., "1.2.3").
        bump_type: The type of bump ("major", "minor", or "patch").

    Returns:
        The new version string.

    Raises:
        ValueError: If the version format is invalid or bump_type is unsupported.
    """
    return Version.from_string(version).new_version(bump_type)


def _get_version(package_name: str) -> str:
    """Get the version of the specified package.

    Args:
        package_name: The name of the package to get the version for.

    Returns:
        A Version instance representing the current version of the package.

    Raises:
        PackageNotFoundError: If the package is not found.
    """
    record = StringIO()
    with redirect_stdout(record):
        cli_get_version([package_name])
    return record.getvalue().strip()


@args_parse()
def cli_get_version(args: CLIArgsType) -> ExitCode:
    """Get the version of the current package.

    Returns:
        The version of the package.
    """
    parser = ArgumentParser(description="Get the version of the package.")
    parser.add_argument("package_name", nargs="?", type=str, help="Name of the package to get the version for.")
    arguments: Namespace = parser.parse_args(args)
    if not arguments.package_name:
        print("No package name provided. Please specify a package name.")
        return ExitCode.FAILURE
    package_name: str = arguments.package_name
    try:
        current_version: str = version(package_name)
        print(current_version)
    except PackageNotFoundError:
        print(f"Package '{package_name}' not found.")
        return ExitCode.FAILURE
    return ExitCode.SUCCESS


def cli_bump(b_type: BumpType, package_name: str, ver: str | tuple[int, int, int]) -> ExitCode:
    """Bump the version of the current package."""
    if b_type not in VALID_BUMP_TYPES:
        print(f"Invalid argument '{b_type}'. Use one of: {', '.join(VALID_BUMP_TYPES)}.")
        return ExitCode.FAILURE

    if isinstance(ver, tuple):
        try:
            parts = Parts(ver)
            version: Version = Version._from_parts(parts)
            new_version = version.new_version(b_type)
            print(str(new_version))
            return ExitCode.SUCCESS
        except ValueError:
            new_version = Version.from_meta(package_name=package_name).new_version(b_type)
            print(str(new_version))
            return ExitCode.SUCCESS
    try:
        new_version: Version = _bump_version(version=ver, bump_type=b_type)
        print(str(new_version))
        return ExitCode.SUCCESS
    except ValueError as e:
        print(f"Error: {e}")
        return ExitCode.FAILURE
    except Exception as e:
        print(f"Unexpected error: {e}")
        return ExitCode.FAILURE
