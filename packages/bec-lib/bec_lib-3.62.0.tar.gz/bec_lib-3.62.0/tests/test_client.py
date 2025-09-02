"""This module tests the bec_lib.client module."""

import pytest

from bec_lib.client import SystemConfig


def test_system_config():
    """Test the SystemConfig class."""
    config = SystemConfig(file_suffix="suff", file_directory="dir")
    assert config.file_suffix == "suff"
    assert config.file_directory == "dir"
    config = SystemConfig()
    assert config.file_suffix is None
    assert config.file_directory is None
    config.file_suffix = "suff_-"
    config.file_directory = "/dir_-/blabla"
    assert config.file_suffix == "suff_-"
    assert config.file_directory == "dir_-/blabla"
    with pytest.raises(ValueError):
        config = SystemConfig(file_suffix="@")
        config = SystemConfig(file_directory="ä")
