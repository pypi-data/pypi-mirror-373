"""
Study module for masster.

This module provides the Sample class for handling mass spectrometry data.
"""

from .study import Study
from . import merge as _  # Import unified merge system  # noqa: F401

__all__ = ["Study"]
