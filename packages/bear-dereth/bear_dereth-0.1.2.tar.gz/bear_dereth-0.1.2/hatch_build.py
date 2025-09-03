"""A custom build hook that uses uv-dynamic-versioning to determine the version and renders a template."""

from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
import sys
from typing import Any, Self

from diskcache import Cache
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from uv_dynamic_versioning import schemas
from uv_dynamic_versioning.base import BasePlugin

path_to_cache: Path = Path.home() / ".cache" / "bear-dereth"
cache = Cache(directory=str(path_to_cache), timeout=60)


@dataclass(slots=True, frozen=True)
class Context:
    version: str
    commit: str
    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version_str: str) -> tuple[int, int, int]:
        """Create a Version instance from a version string.

        Args:
            version_str: A version string in the format "major.minor.patch".

        Returns:
            A Version instance.

        Raises:
            ValueError: If the version string is not in the correct format.
        """

        def part_check[T](n: int, data: tuple, expected_type: Callable[[str], T] = int) -> tuple[T, ...]:
            """Check if the tuple has the correct number of parts."""
            if len(data) != n:
                raise ValueError(f"Version string must have {n} parts: {data!r}")
            values = []
            for i, part in enumerate(data):
                try:
                    values.append(expected_type(part))
                except ValueError as e:
                    raise TypeError(f"Part {i} must be of type {expected_type.__name__}: {part}") from e
            return tuple(values)

        try:
            if "-" in version_str:
                version_str = version_str.split("-")[0]
            if "+" in version_str:
                version_str = version_str.split("+")[0]
            major, minor, patch = part_check(n=3, data=tuple(version_str.split(".")))
            return int(major), int(minor), int(patch)
        except ValueError as e:
            raise ValueError(
                f"Invalid version string format: {version_str}. Expected integers for major, minor, and patch."
            ) from e

    @classmethod
    def from_version(cls, version) -> Self:  # noqa: ANN001
        """A factory method to create a Context from a dunamai Version object."""
        ver: tuple[int, int, int] = cls.from_string(version.base)
        return cls(
            version=version.base,
            commit=version.commit or "",
            major=ver[0],
            minor=ver[1],
            patch=ver[2],
        )


@cache.memoize()
def _get_version(config: schemas.UvDynamicVersioning) -> dict[str, int | str]:
    """Get version from VCS with caching."""
    from dunamai import Version  # noqa: PLC0415

    try:
        value: Version = Version.from_vcs(
            config.vcs,
            latest_tag=config.latest_tag,
            strict=config.strict,
            tag_branch=config.tag_branch,
            tag_dir=config.tag_dir,
            full_commit=config.full_commit,
            ignore_untracked=config.ignore_untracked,
            pattern=config.pattern,
            pattern_prefix=config.pattern_prefix,
            commit_length=config.commit_length,
        )
        return asdict(Context.from_version(value))
    except RuntimeError:
        if config.fallback_version:
            return asdict(Context.from_version(Version(config.fallback_version)))
        raise


def get_value[T](config: dict[str, Any], key: str, key_type: Callable[[str], T]) -> T:
    """Get a value from the config dictionary and convert it to the specified type."""
    value = config.get(key)
    if value is None:
        raise ValueError(f"Missing required configuration key: {key}")
    return key_type(value)


class CustomBuildHook(BasePlugin, BuildHookInterface):
    PLUGIN_NAME = "custom"

    def _output_version(self, version: dict[str, int | str], output_path: Path) -> None:
        from jinja2 import Template  # noqa: PLC0415

        template_str: str = get_value(self.config, "template", str)
        template = Template(template_str)
        rendered_content: str = template.render(**version)
        output_path.write_text(rendered_content)

    def initialize(self, _: str, __: dict[str, Any]) -> None:  # type: ignore[override]
        """Initialize the build hook."""
        output_path: Path = get_value(self.config, "output", Path)
        if not output_path.parent.exists():
            print("Cannot find parent directory for output path...exiting.", sys.stderr)
            return

        version: dict[str, int | str] = _get_version(self.project_config)
        self._output_version(version, output_path)
