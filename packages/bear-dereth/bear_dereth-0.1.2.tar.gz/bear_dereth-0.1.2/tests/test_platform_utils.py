from unittest.mock import patch

from bear_dereth.tools.platform_utils import DARWIN, LINUX, WINDOWS, get_platform, is_linux, is_macos, is_windows


@patch("platform.system", return_value="Darwin")
def test_macos(mock_system):
    assert get_platform() == DARWIN
    assert is_macos()
    assert not is_windows()
    assert not is_linux()


@patch("platform.system", return_value="Windows")
def test_windows(mock_system):
    assert get_platform() == WINDOWS
    assert is_windows()
    assert not is_macos()
    assert not is_linux()


@patch("platform.system", return_value="Linux")
def test_linux(mock_system):
    assert get_platform() == LINUX
    assert is_linux()
    assert not is_macos()
    assert not is_windows()


@patch("platform.system", return_value="FakeOS")
def test_other(mock_system):
    assert get_platform() == "Other"
    assert not is_macos()
    assert not is_windows()
    assert not is_linux()
