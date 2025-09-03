"""A utility to create slugs from strings."""

import re
import unicodedata


def slugify(value: str, sep: str = "-") -> str:
    """Return an ASCII slug for ``value``.

    Args:
        value: String to normalize.
        sep: Character used to replace whitespace and punctuation.

    Returns:
        A sluggified version of ``value``.
    """
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-_\s]+", sep, value).strip("-_")
