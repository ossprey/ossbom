import pytest

from .dependency_env import DependencyEnv


def test_dependency_env_values():
    """Test that DependencyEnv has the expected values."""
    assert DependencyEnv.DEV.value == "dev"
    assert DependencyEnv.PROD.value == "prod"


def test_dependency_env_from_string():
    """Test creating a DependencyEnv from its string value."""
    assert DependencyEnv("dev") == DependencyEnv.DEV
    assert DependencyEnv("prod") == DependencyEnv.PROD


def test_dependency_env_invalid_value_raises():
    """Test that an invalid value raises a ValueError."""
    with pytest.raises(ValueError):
        DependencyEnv("invalid")


def test_dependency_env_members():
    """Test that DependencyEnv contains exactly the expected members."""
    members = {e.value for e in DependencyEnv}
    assert members == {"dev", "prod"}
