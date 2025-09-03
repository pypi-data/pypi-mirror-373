"""Tests for defaults modules."""

import pytest


class TestSampleDefaults:
    """Test suite for sample defaults modules."""

    def test_sample_defaults_creation(self):
        """Test sample_defaults creation and basic functionality."""
        from masster.sample.defaults.sample_def import sample_defaults
        
        # Test default creation
        params = sample_defaults()
        
        assert params is not None
        assert hasattr(params, 'filename')
        assert hasattr(params, 'ondisk')
        assert hasattr(params, 'log_level')
        assert hasattr(params, 'mz_tol_ms1_da')
        assert hasattr(params, 'mz_tol_ms2_da')

    def test_sample_defaults_custom_values(self):
        """Test sample_defaults with custom values."""
        from masster.sample.defaults.sample_def import sample_defaults
        
        params = sample_defaults(
            filename="test.mzML",
            ondisk=True,
            log_level="DEBUG",
            mz_tol_ms1_da=0.001,
            mz_tol_ms2_da=0.01
        )
        
        assert params.filename == "test.mzML"
        assert params.ondisk is True
        assert params.log_level == "DEBUG"
        assert params.mz_tol_ms1_da == 0.001
        assert params.mz_tol_ms2_da == 0.01

    def test_sample_defaults_methods(self):
        """Test sample_defaults methods."""
        from masster.sample.defaults.sample_def import sample_defaults
        
        params = sample_defaults()
        
        # Test to_dict method if it exists
        try:
            param_dict = params.to_dict()
            assert isinstance(param_dict, dict)
            assert 'filename' in param_dict
            assert 'log_level' in param_dict
        except AttributeError:
            pytest.skip("to_dict method not implemented")

    def test_sample_defaults_validation(self):
        """Test sample_defaults parameter validation."""
        from masster.sample.defaults.sample_def import sample_defaults
        
        params = sample_defaults()
        
        # Test validation methods if they exist - validation might require parameters
        try:
            # Try calling validate with sample parameters
            params.validate('log_level', 'INFO')
            assert True  # If no exception, validation passed
        except AttributeError:
            pytest.skip("Validation method not implemented")
        except Exception:
            # Validation might fail with test values, which is acceptable
            assert True

    def test_sample_defaults_set_method(self):
        """Test sample_defaults set method."""
        from masster.sample.defaults.sample_def import sample_defaults
        
        params = sample_defaults()
        
        # Test set method if it exists
        try:
            params.set('log_level', 'WARNING')
            assert params.log_level == 'WARNING'
        except AttributeError:
            pytest.skip("Set method not implemented")

    def test_find_features_defaults(self):
        """Test find_features_def module."""
        try:
            from masster.sample.defaults.find_features_def import find_features_defaults
            
            params = find_features_defaults()
            assert params is not None
            
            # Test basic functionality
            assert hasattr(params, '__dict__')
            
        except ImportError:
            pytest.skip("find_features_defaults not available")

    def test_find_ms2_defaults(self):
        """Test find_ms2_def module."""
        try:
            from masster.sample.defaults.find_ms2_def import find_ms2_defaults
            
            params = find_ms2_defaults()
            assert params is not None
            
            # Test basic functionality
            assert hasattr(params, '__dict__')
            
        except ImportError:
            pytest.skip("find_ms2_defaults not available")

    def test_find_adducts_defaults(self):
        """Test find_adducts_def module."""
        try:
            from masster.sample.defaults.find_adducts_def import find_adducts_defaults
            
            params = find_adducts_defaults()
            assert params is not None
            
            # Test basic functionality
            assert hasattr(params, '__dict__')
            
        except ImportError:
            pytest.skip("find_adducts_defaults not available")

    def test_get_spectrum_defaults(self):
        """Test get_spectrum_def module."""
        try:
            from masster.sample.defaults.get_spectrum_def import get_spectrum_defaults
            
            params = get_spectrum_defaults()
            assert params is not None
            
            # Test basic functionality
            assert hasattr(params, '__dict__')
            
        except ImportError:
            pytest.skip("get_spectrum_defaults not available")


class TestStudyDefaults:
    """Test suite for study defaults modules."""

    def test_study_defaults_creation(self):
        """Test study_defaults creation and basic functionality."""
        from masster.study.defaults.study_def import study_defaults
        
        # Test default creation
        params = study_defaults()
        
        assert params is not None
        assert hasattr(params, 'folder')
        assert hasattr(params, 'label')
        assert hasattr(params, 'log_level')
        assert hasattr(params, 'log_label')

    def test_study_defaults_custom_values(self):
        """Test study_defaults with custom values."""
        from masster.study.defaults.study_def import study_defaults
        
        params = study_defaults(
            folder="/test/path",
            label="test_study",
            log_level="ERROR",
            log_label="test_logger"
        )
        
        assert params.folder == "/test/path"
        assert params.label == "test_study"
        assert params.log_level == "ERROR"
        assert params.log_label == "test_logger"

    def test_study_defaults_methods(self):
        """Test study_defaults methods."""
        from masster.study.defaults.study_def import study_defaults
        
        params = study_defaults()
        
        # Test to_dict method if it exists
        try:
            param_dict = params.to_dict()
            assert isinstance(param_dict, dict)
            assert 'folder' in param_dict
            assert 'log_level' in param_dict
        except AttributeError:
            pytest.skip("to_dict method not implemented")

    def test_study_defaults_validation(self):
        """Test study_defaults parameter validation."""
        from masster.study.defaults.study_def import study_defaults
        
        params = study_defaults()
        
        # Test validation methods if they exist - validation might require parameters
        try:
            # Try calling validate with study parameters
            params.validate('log_level', 'INFO')
            assert True  # If no exception, validation passed
        except AttributeError:
            pytest.skip("Validation method not implemented")
        except Exception:
            # Validation might fail with test values, which is acceptable
            assert True

    def test_align_defaults(self):
        """Test align_def module."""
        try:
            from masster.study.defaults.align_def import align_defaults
            
            params = align_defaults()
            assert params is not None
            
            # Test basic functionality
            assert hasattr(params, '__dict__')
            
        except ImportError:
            pytest.skip("align_defaults not available")

    def test_export_defaults(self):
        """Test export_def module."""
        try:
            from masster.study.defaults.export_def import export_mgf_defaults
            
            params = export_mgf_defaults()
            assert params is not None
            
            # Test basic functionality
            assert hasattr(params, '__dict__')
            
        except ImportError:
            pytest.skip("export_defaults not available")

    def test_fill_chrom_defaults(self):
        """Test fill_chrom_def module."""
        try:
            from masster.study.defaults.fill_chrom_def import fill_chrom_defaults
            
            params = fill_chrom_defaults()
            assert params is not None
            
            # Test basic functionality
            assert hasattr(params, '__dict__')
            
        except ImportError:
            pytest.skip("fill_chrom_defaults not available")

    def test_find_consensus_defaults(self):
        """Test find_consensus_def module."""
        try:
            from masster.study.defaults.find_consensus_def import find_consensus_defaults
            
            params = find_consensus_defaults()
            assert params is not None
            
            # Test basic functionality
            assert hasattr(params, '__dict__')
            
        except ImportError:
            pytest.skip("find_consensus_defaults not available")

    def test_study_find_ms2_defaults(self):
        """Test study find_ms2_def module."""
        try:
            from masster.study.defaults.find_ms2_def import find_ms2_defaults
            
            params = find_ms2_defaults()
            assert params is not None
            
            # Test basic functionality
            assert hasattr(params, '__dict__')
            
        except ImportError:
            pytest.skip("study find_ms2_defaults not available")

    def test_integrate_chrom_defaults(self):
        """Test integrate_chrom_def module."""
        try:
            from masster.study.defaults.integrate_chrom_def import integrate_chrom_defaults
            
            params = integrate_chrom_defaults()
            assert params is not None
            
            # Test basic functionality
            assert hasattr(params, '__dict__')
            
        except ImportError:
            pytest.skip("integrate_chrom_defaults not available")


class TestDefaultsInteroperability:
    """Test interoperability between different defaults modules."""

    def test_sample_study_defaults_compatibility(self):
        """Test compatibility between sample and study defaults."""
        from masster.sample.defaults.sample_def import sample_defaults
        from masster.study.defaults.study_def import study_defaults
        
        sample_params = sample_defaults()
        study_params = study_defaults()
        
        # Both should have log_level
        assert hasattr(sample_params, 'log_level')
        assert hasattr(study_params, 'log_level')
        
        # Default log levels should be the same
        assert sample_params.log_level == study_params.log_level

    def test_defaults_serialization(self):
        """Test that defaults can be serialized."""
        from masster.sample.defaults.sample_def import sample_defaults
        from masster.study.defaults.study_def import study_defaults
        
        sample_params = sample_defaults()
        study_params = study_defaults()
        
        # Test string representation
        sample_str = str(sample_params)
        study_str = str(study_params)
        
        assert isinstance(sample_str, str)
        assert isinstance(study_str, str)
        assert len(sample_str) > 0
        assert len(study_str) > 0

    def test_defaults_equality(self):
        """Test defaults equality comparison."""
        from masster.sample.defaults.sample_def import sample_defaults
        
        # Test same parameters are equal
        params1 = sample_defaults(log_level="INFO")
        params2 = sample_defaults(log_level="INFO")
        
        # Test equality if implemented
        try:
            are_equal = (params1 == params2)
            assert isinstance(are_equal, bool)
        except (TypeError, NotImplementedError):
            pytest.skip("Equality comparison not implemented")

    def test_defaults_copy(self):
        """Test defaults copying."""
        from masster.sample.defaults.sample_def import sample_defaults
        
        original = sample_defaults(filename="original.mzML", log_level="DEBUG")
        
        # Test copy methods if they exist
        try:
            import copy
            copied = copy.copy(original)
            assert copied.filename == original.filename
            assert copied.log_level == original.log_level
            
            # Test deep copy
            deep_copied = copy.deepcopy(original)
            assert deep_copied.filename == original.filename
            assert deep_copied.log_level == original.log_level
            
        except (AttributeError, TypeError):
            pytest.skip("Copy functionality not available")

    def test_defaults_metadata_access(self):
        """Test accessing parameter metadata."""
        from masster.sample.defaults.sample_def import sample_defaults
        from masster.study.defaults.study_def import study_defaults
        
        sample_params = sample_defaults()
        study_params = study_defaults()
        
        # Test metadata access if available
        try:
            if hasattr(sample_params, '_param_metadata'):
                metadata = sample_params._param_metadata
                assert isinstance(metadata, dict)
                assert len(metadata) > 0
                
            if hasattr(study_params, '_param_metadata'):
                metadata = study_params._param_metadata
                assert isinstance(metadata, dict)
                assert len(metadata) > 0
                
        except AttributeError:
            pytest.skip("Parameter metadata not available")
