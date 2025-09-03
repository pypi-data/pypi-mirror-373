"""Integration tests for package functionality."""

import pytest
import numpy as np


class TestPackageIntegration:
    """Integration tests for the masster package."""

    def test_basic_workflow(self):
        """Test a basic spectrum processing workflow."""
        from masster.spectrum import Spectrum
        
        # Create sample data
        mz = np.array([100.0, 150.0, 200.0, 250.0, 300.0])
        intensity = np.array([1000, 5000, 3000, 800, 1200])
        
        # Create spectrum
        spectrum = Spectrum(mz=mz, inty=intensity, ms_level=1, label="test_spectrum")
        
        # Test processing chain
        processed = (spectrum
                     .copy()
                     .trim(mz_min=120.0, mz_max=280.0)
                     .keep_top(n=3)
                     .scale(factor=1.5))
        
        # Verify results
        assert len(processed) == 3
        assert processed.mz_min() >= 120.0
        assert processed.mz_max() <= 280.0
        assert np.max(processed.inty) == 5000 * 1.5  # Scaled highest peak
        assert "s[1.5]" in processed.history

    def test_combine_peaks_functionality(self):
        """Test peak combination functionality."""
        from masster.spectrum import Spectrum, combine_peaks
        
        # Create two spectra with overlapping peaks
        mz1 = np.array([100.0, 150.0, 200.0])
        intensity1 = np.array([1000, 2000, 3000])
        spec1 = Spectrum(mz=mz1, inty=intensity1, ms_level=1)
        
        mz2 = np.array([100.1, 149.9, 250.0])  # Slightly shifted peaks
        intensity2 = np.array([1500, 2500, 1000])
        spec2 = Spectrum(mz=mz2, inty=intensity2, ms_level=1)
        
        # Combine spectra
        combined = combine_peaks([spec1, spec2], tolerance=0.2, ppm=0)
        
        # Should have combined overlapping peaks
        assert len(combined) <= len(spec1) + len(spec2)
        assert combined.centroided is True

    def test_serialization_roundtrip(self):
        """Test that spectra can be serialized and deserialized."""
        from masster.spectrum import Spectrum
        
        # Create complex spectrum with additional attributes
        mz = np.array([100.0, 150.0, 200.0])
        intensity = np.array([1000, 2000, 3000])
        
        original = Spectrum(mz=mz, inty=intensity, ms_level=2, label="ms2_spectrum")
        original.history = "test_history"
        
        # Serialize and deserialize
        data = original.to_dict()
        reconstructed = Spectrum.from_dict(data)
        
        # Verify all attributes are preserved
        assert np.array_equal(reconstructed.mz, original.mz)
        assert np.array_equal(reconstructed.inty, original.inty)
        assert reconstructed.ms_level == original.ms_level
        assert reconstructed.label == original.label
        assert reconstructed.history == original.history

    def test_parameter_usage(self):
        """Test that parameters can be used in processing."""
        try:
            from masster.sample.defaults.sample_def import sample_defaults
            from masster.study.defaults.study_def import study_defaults
            
            # Test parameter instantiation
            sample_params = sample_defaults()
            study_params = study_defaults()
            
            # Verify parameters have expected structure
            assert hasattr(sample_params, 'mz_tol_ms1_da')
            assert hasattr(sample_params, 'mz_tol_ms2_da')
            assert hasattr(sample_params, 'log_level')
            assert hasattr(study_params, 'folder')
            assert hasattr(study_params, 'log_level')
            
            # Verify default values
            assert sample_params.mz_tol_ms1_da == 0.002
            assert sample_params.log_level == "INFO"
            assert study_params.log_level == "INFO"
            
        except ImportError as e:
            pytest.skip(f"Parameter modules not available: {e}")

    def test_data_directory_access(self):
        """Test that sample defaults can be accessed."""
        try:
            from masster.sample.defaults.sample_def import sample_defaults
            
            params = sample_defaults()
            
            # Check that parameters have expected attributes
            assert hasattr(params, 'filename')
            assert hasattr(params, 'ondisk')
            assert hasattr(params, 'label')
            
            # Check default values
            assert params.filename is None
            assert params.ondisk is False
            
        except ImportError as e:
            pytest.skip(f"Filename parameters not available: {e}")

    def test_ensure_package_structure(self):
        """Test that package has expected structure."""
        import masster
        
        # Check main package attributes
        required_attrs = ['__version__', 'Spectrum', 'Sample', 'Study', 'Chromatogram']
        for attr in required_attrs:
            assert hasattr(masster, attr), f"Package missing required attribute: {attr}"
        
        # Check that version is accessible
        assert isinstance(masster.__version__, str)
        assert len(masster.__version__) > 0
