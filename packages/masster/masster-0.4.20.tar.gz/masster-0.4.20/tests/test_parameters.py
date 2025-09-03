"""Tests for parameter modules."""

import pytest


def test_sample_defaults_import():
    """Test that sample_defaults can be imported and instantiated."""
    try:
        from masster.sample.defaults.sample_def import sample_defaults
        
        # Test default instantiation
        params = sample_defaults()
        assert params is not None
        
        # Test that it has expected attributes
        assert hasattr(params, 'filename')
        assert hasattr(params, 'mz_tol_ms1_da')
        assert hasattr(params, 'mz_tol_ms2_da')
        assert hasattr(params, 'log_level')
        
        # Test default values
        assert params.mz_tol_ms1_da == 0.002
        assert params.mz_tol_ms2_da == 0.005
        assert params.log_level == "INFO"
        
    except ImportError as e:
        pytest.fail(f"Failed to import sample_defaults: {e}")


def test_study_defaults_import():
    """Test that study_defaults can be imported and instantiated."""
    try:
        from masster.study.defaults.study_def import study_defaults
        
        # Test default instantiation
        params = study_defaults()
        assert params is not None
        
        # Test that it has expected attributes
        assert hasattr(params, 'folder')
        assert hasattr(params, 'label')
        assert hasattr(params, 'log_level')
        assert hasattr(params, 'log_label')
        
        # Test default values
        assert params.log_level == "INFO"
        assert params.folder is None
        
    except ImportError as e:
        pytest.fail(f"Failed to import study_defaults: {e}")


def test_sample_parameters_functions():
    """Test that sample parameter functions can be imported."""
    try:
        from masster.sample.parameters import (
            store_history,
            get_parameters,
            update_parameters,
            get_parameters_property,
            set_parameters_property
        )
        assert store_history is not None
        assert get_parameters is not None
        assert update_parameters is not None
        assert get_parameters_property is not None
        assert set_parameters_property is not None
        
    except ImportError as e:
        pytest.fail(f"Failed to import sample parameter functions: {e}")


def test_study_parameters_functions():
    """Test that study parameter functions can be imported."""
    try:
        from masster.study.parameters import (
            store_history,
            get_parameters,
            update_parameters,
            get_parameters_property,
            set_parameters_property
        )
        assert store_history is not None
        assert get_parameters is not None
        assert update_parameters is not None
        assert get_parameters_property is not None
        assert set_parameters_property is not None
        
    except ImportError as e:
        pytest.fail(f"Failed to import study parameter functions: {e}")


def test_defaults_submodules_import():
    """Test that defaults submodules can be imported."""
    try:
        # Test sample defaults submodules
        from masster.sample.defaults import find_features_def, find_ms2_def, find_adducts_def
        assert find_features_def is not None
        assert find_ms2_def is not None
        assert find_adducts_def is not None
        
        # Test study defaults submodules  
        from masster.study.defaults import align_def, export_def, fill_chrom_def
        assert align_def is not None
        assert export_def is not None
        assert fill_chrom_def is not None
        
    except ImportError as e:
        pytest.fail(f"Failed to import defaults submodules: {e}")
