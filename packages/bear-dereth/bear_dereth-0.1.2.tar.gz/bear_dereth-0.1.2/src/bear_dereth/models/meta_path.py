"""Module providing a WrappedPath class for enhanced Path handling and metadata extraction."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class WrappedPath(BaseModel):
    """A class to wrap a Path object and provide additional attributes and methods.

    This for easily serializing Path objects and getting useful metadata for external use.
    """

    path: Path
    parent: dict = Field(default_factory=dict, description="Recursive parent directories")
    name: str = Field(default="", description="The name of the file or directory like 'file.txt'")
    suffix: str = Field(default="", description="The file extension, if any like '.txt'")
    stem: str = Field(default="", description="The name of the file without the suffix, like 'file'")
    absolute: Path = Field(default=Path(), description="The absolute path of the file or directory")
    is_absolute: bool = Field(default=False, description="Whether the path is absolute")
    exists: bool = Field(default=False, description="Whether the path exists")
    is_dir: bool = Field(default=False, description="Whether the path is a directory")
    is_file: bool = Field(default=False, description="Whether the path is a file")
    is_symlink: bool = Field(default=False, description="Whether the path is a symbolic link")
    is_mount: bool = Field(default=False, description="Whether the path is a mount point")
    parts: list[str] = Field(default_factory=list, description="The parts of the path as a list")
    as_uri: str = Field(default="", description="The URI representation of the path")
    modified: int = Field(default=0, description="The last modified time of the file or directory")
    modified_str: str = Field(default="", description="The last modified time as a string")
    created: int = Field(default=0, description="The creation time of the file or directory")
    created_str: str = Field(default="", description="The creation time as a string")
    file_size: int = Field(default=0, description="The size of the file in bytes")

    @field_validator("path", mode="before")
    @classmethod
    def validate_path(cls, v: Any) -> Path:
        """Validate and convert the input to a Path object."""
        if isinstance(v, str):
            v = Path(v)
        if isinstance(v, Path):
            return v.expanduser().resolve()
        raise TypeError(f"Path must be a str or Path object, got {type(v)}")

    def recursive_parents(self) -> dict[str, WrappedPath]:
        """Get immediate parent with its own parent chain."""
        if self.path.parent == self.path:
            return {}

        immediate_parent = WrappedPath(path=self.path.parent)
        return {str(self.path.parent): immediate_parent}

    def model_post_init(self, context: Any) -> None:
        """Post-initialization method to set attributes based on the path."""
        try:
            from bear_epoch_time import EpochTimestamp  # noqa: PLC0415 # type: ignore[import]
        except ImportError:

            class EpochTimestamp(int):
                def __init__(self, ms: int):
                    self.ms: int = ms

                def to_string(self) -> str:
                    return "N/A"

        self.name = self.path.name
        self.suffix = self.path.suffix
        self.stem = self.path.stem
        self.parent = self.recursive_parents()
        self.absolute = self.path.resolve()
        self.is_absolute = self.path.is_absolute()
        self.exists = self.path.exists()
        self.is_dir = self.path.is_dir()
        self.is_file = self.path.is_file()
        self.is_symlink = self.path.is_symlink()
        self.is_mount = self.path.is_mount()
        self.parts = list(self.path.parts)
        self.as_uri = self.path.as_uri()
        self.modified = EpochTimestamp(int(self.path.stat().st_mtime if self.exists else 0.0) * 1000)
        self.modified_str = self.modified.to_string()
        self.created = EpochTimestamp(int(self.path.stat().st_ctime if self.exists else 0.0) * 1000)
        self.created_str = self.created.to_string()
        self.file_size = self.path.stat().st_size if self.is_file else 0
        return super().model_post_init(context)

    def __str__(self) -> str:
        """Return a string representation of the WrappedPath instance."""
        return self.model_dump_json(indent=4, exclude_none=True)
