"""Tests for masster package initialization and imports."""

import pytest


def test_package_imports():
    """Test that main package components can be imported."""
    try:
        import masster
        assert hasattr(masster, '__version__')
        assert masster.__version__ is not None
    except ImportError as e:
        pytest.fail(f"Failed to import masster package: {e}")


def test_version_access():
    """Test that version can be accessed through different methods."""
    import masster
    from masster._version import __version__, get_version
    
    # Test version consistency
    assert masster.__version__ == __version__
    assert get_version() == __version__
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_main_classes_importable():
    """Test that main classes can be imported."""
    try:
        from masster import Spectrum, Sample, Chromatogram
        
        # Check that classes are actually classes
        assert callable(Spectrum)
        assert callable(Sample)
        assert callable(Chromatogram)
        
    except ImportError as e:
        pytest.fail(f"Failed to import main classes: {e}")


def test_submodule_imports():
    """Test that submodules can be imported."""
    try:
        from masster import spectrum, sample, chromatogram
        
        # Test that modules have expected attributes
        assert hasattr(spectrum, 'Spectrum')
        assert hasattr(sample, 'Sample')
        assert hasattr(chromatogram, 'Chromatogram')
        
    except ImportError as e:
        pytest.fail(f"Failed to import submodules: {e}")


def test_parameters_import():
    """Test that parameter modules can be imported."""
    try:
        from masster.sample.parameters import (
            store_history as sample_store_history,
            get_parameters as sample_get_parameters,
            update_parameters as sample_update_parameters
        )
        from masster.study.parameters import (
            store_history as study_store_history,
            get_parameters as study_get_parameters,
            update_parameters as study_update_parameters
        )
        assert sample_store_history is not None
        assert sample_get_parameters is not None
        assert sample_update_parameters is not None
        assert study_store_history is not None
        assert study_get_parameters is not None
        assert study_update_parameters is not None
    except ImportError as e:
        pytest.fail(f"Failed to import parameters: {e}")
