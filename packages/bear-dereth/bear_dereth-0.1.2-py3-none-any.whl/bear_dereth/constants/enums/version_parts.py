"""A module defining enumerations for version parts."""

from bear_dereth.tools.rich_enums import IntValue, RichIntEnum


class VersionParts(RichIntEnum):
    """Enumeration for version parts."""

    MAJOR = IntValue(value=0, text="major")
    MINOR = IntValue(value=1, text="minor")
    PATCH = IntValue(value=2, text="patch")

    @classmethod
    def choices(cls) -> list[str]:
        """Return a list of valid version parts."""
        return [version_part.text for version_part in cls]

    @classmethod
    def parts(cls) -> int:
        """Return the total number of version parts."""
        return len(cls.choices())


VALID_BUMP_TYPES: list[str] = VersionParts.choices()
ALL_PARTS: int = VersionParts.parts()


__all__ = ["ALL_PARTS", "VALID_BUMP_TYPES", "VersionParts"]
