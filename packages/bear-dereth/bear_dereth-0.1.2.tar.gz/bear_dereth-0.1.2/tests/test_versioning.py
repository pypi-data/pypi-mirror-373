import pytest

from bear_dereth.tools.versioning import Version


def test_trailing_dash_and_plus():
    ver = "1.2.3-"
    v9: Version = Version.from_string(ver)
    assert v9.major == 1
    assert v9.minor == 2
    assert v9.patch == 3
    assert v9.post is None
    assert str(v9) == "1.2.3"

    ver = "1.2.3+"
    v10: Version = Version.from_string(ver)
    assert v10.major == 1
    assert v10.minor == 2
    assert v10.patch == 3
    assert v10.post is None
    assert str(v10) == "1.2.3"


def test_double_dots():
    ver = "1..2.3"
    v6: Version = Version.from_string(ver)
    assert v6.major == 1
    assert v6.minor == 2
    assert v6.patch == 3
    assert v6.post is None
    assert str(v6) == "1.2.3"


def test_trailing_dot_and_leading_dot():
    ver = "1.2.3."
    v7: Version = Version.from_string(ver)
    assert v7.major == 1
    assert v7.minor == 2
    assert v7.patch == 3
    assert v7.post is None
    assert str(v7) == "1.2.3"

    ver = ".1.2.3"
    v8: Version = Version.from_string(ver)
    assert v8.major == 1
    assert v8.minor == 2
    assert v8.patch == 3
    assert v8.post is None
    assert str(v8) == "1.2.3"


def test_multiple_parts():
    ver = "v2.1.0-alpha.1+build.2023.01.15"
    v1: Version = Version.from_string(ver)
    assert v1.major == 2
    assert v1.minor == 1
    assert v1.patch == 0
    assert v1.post is None
    assert str(v1) == "2.1.0"

    ver = "3.14.159-rc.1.2+build.jenkins.456"
    v3: Version = Version.from_string(ver)
    assert v3.major == 3
    assert v3.minor == 14
    assert v3.patch == 159
    assert v3.post is None
    assert str(v3) == "3.14.159"

    ver = "1.2.3.post1-dev+local.dirty"
    v4: Version = Version.from_string(ver)
    assert v4.major == 1
    assert v4.minor == 2
    assert v4.patch == 3
    assert v4.post == "post1"
    assert str(v4) == "1.2.3.post1"


def test_multiple_dots_in_post():
    ver = "1.2.3.post1.dev2"
    v5: Version = Version.from_string(ver)
    assert v5.major == 1
    assert v5.minor == 2
    assert v5.patch == 3
    assert v5.post == "post1"
    assert str(v5) == "1.2.3.post1"

    ver = "1.2.3.4.5.6"
    v11: Version = Version.from_string(ver)
    assert v11.major == 1
    assert v11.minor == 2
    assert v11.patch == 3
    assert v11.post == "4"
    assert str(v11) == "1.2.3.4"


def test_invalid_versions() -> None:
    """Test invalid version strings."""
    with pytest.raises(ValueError, match="Invalid number of parts. Expected 3 or 4 parts:"):
        Version.from_string("1.2")

    with pytest.raises(ValueError, match="invalid literal"):
        Version.from_string("version.2.3")

    with pytest.raises(ValueError, match="invalid literal"):
        Version.from_string("1.two.3")
