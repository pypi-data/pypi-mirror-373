"""Tests for version module functionality."""

from masster._version import __version__, get_version, main
from io import StringIO
import sys


def test_version_string():
    """Test that version is a valid string."""
    assert isinstance(__version__, str)
    assert len(__version__) > 0
    assert "." in __version__  # Should contain at least one dot for semantic versioning


def test_get_version_function():
    """Test get_version function returns correct version."""
    version = get_version()
    assert version == __version__
    assert isinstance(version, str)


def test_version_format():
    """Test that version follows semantic versioning pattern."""
    import re
    
    # Basic semantic versioning pattern (x.y.z with optional pre-release)
    pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9\-\.]+)?$'
    assert re.match(pattern, __version__), f"Version '{__version__}' doesn't follow semantic versioning"


def test_main_function():
    """Test the main function prints version correctly."""
    # Capture stdout
    captured_output = StringIO()
    sys.stdout = captured_output
    
    try:
        main()
        output = captured_output.getvalue()
        assert f"Current version: {__version__}" in output
    finally:
        sys.stdout = sys.__stdout__


def test_version_consistency():
    """Test version consistency across different access methods."""
    import masster
    
    # All version access methods should return the same value
    assert masster.__version__ == __version__
    assert get_version() == __version__
