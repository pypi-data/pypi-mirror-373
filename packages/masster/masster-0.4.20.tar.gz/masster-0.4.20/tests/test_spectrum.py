"""Tests for Spectrum class functionality."""

import pytest
import numpy as np
from masster.spectrum import Spectrum


class TestSpectrum:
    """Test cases for Spectrum class."""

    def test_spectrum_creation(self):
        """Test basic spectrum creation."""
        mz = np.array([100.0, 150.0, 200.0, 250.0])
        intensity = np.array([1000, 5000, 3000, 800])
        
        spectrum = Spectrum(mz=mz, inty=intensity)
        
        assert len(spectrum.mz) == 4
        assert len(spectrum.inty) == 4
        assert np.array_equal(spectrum.mz, mz)
        assert np.array_equal(spectrum.inty, intensity)

    def test_spectrum_with_invalid_dimensions(self):
        """Test spectrum creation with mismatched array dimensions."""
        mz = np.array([100.0, 150.0, 200.0])
        intensity = np.array([1000, 5000])  # Different length
        
        with pytest.raises(ValueError, match="mz and intensity arrays must have the same shape"):
            Spectrum(mz=mz, inty=intensity)

    def test_spectrum_copy(self):
        """Test spectrum copying functionality."""
        mz = np.array([100.0, 150.0, 200.0])
        intensity = np.array([1000, 5000, 3000])
        
        original = Spectrum(mz=mz, inty=intensity, ms_level=1, label="test")
        copy_spec = original.copy()
        
        # Check that arrays are copied, not referenced
        assert np.array_equal(copy_spec.mz, original.mz)
        assert np.array_equal(copy_spec.inty, original.inty)
        assert copy_spec.mz is not original.mz
        assert copy_spec.inty is not original.inty
        
        # Check that attributes are copied
        assert copy_spec.ms_level == original.ms_level
        assert copy_spec.label == original.label

    def test_spectrum_trim(self):
        """Test m/z trimming functionality."""
        mz = np.array([100.0, 150.0, 200.0, 250.0, 300.0])
        intensity = np.array([1000, 5000, 3000, 800, 1200])
        
        spectrum = Spectrum(mz=mz, inty=intensity)
        
        # Test trimming with min and max
        trimmed = spectrum.copy().trim(mz_min=150.0, mz_max=250.0)
        
        expected_mz = np.array([150.0, 200.0, 250.0])
        expected_inty = np.array([5000, 3000, 800])
        
        assert np.array_equal(trimmed.mz, expected_mz)
        assert np.array_equal(trimmed.inty, expected_inty)

    def test_spectrum_properties(self):
        """Test spectrum property methods."""
        mz = np.array([100.0, 150.0, 200.0, 250.0])
        intensity = np.array([1000, 5000, 3000, 800])
        
        spectrum = Spectrum(mz=mz, inty=intensity)
        
        assert spectrum.mz_min() == 100.0
        assert spectrum.mz_max() == 250.0
        assert spectrum.inty_min() == 800
        assert spectrum.inty_max() == 5000
        assert spectrum.tic() == 9800  # Sum of intensities

    def test_empty_spectrum(self):
        """Test empty spectrum handling."""
        spectrum = Spectrum(mz=np.array([]), inty=np.array([]))
        
        assert len(spectrum) == 0
        assert spectrum.mz_min() == 0
        assert spectrum.mz_max() == 0
        assert spectrum.inty_min() == 0
        assert spectrum.inty_max() == 0
        assert spectrum.tic() == 0

    def test_spectrum_keep_top(self):
        """Test keeping top N peaks."""
        mz = np.array([100.0, 150.0, 200.0, 250.0, 300.0])
        intensity = np.array([1000, 5000, 3000, 800, 1200])
        
        spectrum = Spectrum(mz=mz, inty=intensity)
        top_3 = spectrum.keep_top(n=3)
        
        # Should keep the 3 highest intensity peaks
        assert len(top_3) == 3
        assert 5000 in top_3.inty  # Highest
        assert 3000 in top_3.inty  # Second highest
        assert 1200 in top_3.inty  # Third highest

    def test_spectrum_scale(self):
        """Test spectrum scaling."""
        mz = np.array([100.0, 150.0, 200.0])
        intensity = np.array([1000, 2000, 3000])
        
        spectrum = Spectrum(mz=mz, inty=intensity)
        scaled = spectrum.scale(factor=2.0)
        
        assert np.array_equal(scaled.mz, spectrum.mz)
        assert np.array_equal(scaled.inty, spectrum.inty * 2.0)
        assert "s[2.0]" in scaled.history

    def test_spectrum_to_dict_from_dict(self):
        """Test spectrum serialization and deserialization."""
        mz = np.array([100.0, 150.0, 200.0])
        intensity = np.array([1000, 2000, 3000])
        
        original = Spectrum(mz=mz, inty=intensity, ms_level=1, label="test")
        
        # Convert to dict and back
        spec_dict = original.to_dict()
        reconstructed = Spectrum.from_dict(spec_dict)
        
        assert np.array_equal(reconstructed.mz, original.mz)
        assert np.array_equal(reconstructed.inty, original.inty)
        assert reconstructed.ms_level == original.ms_level
        assert reconstructed.label == original.label

    def test_spectrum_pandalize(self):
        """Test conversion to pandas DataFrame."""
        mz = np.array([100.0, 150.0, 200.0])
        intensity = np.array([1000, 2000, 3000])
        
        spectrum = Spectrum(mz=mz, inty=intensity)
        df = spectrum.pandalize()
        
        assert len(df) == 3
        assert 'mz' in df.columns
        assert 'inty' in df.columns
        assert np.array_equal(df['mz'].values, mz)
        assert np.array_equal(df['inty'].values, intensity)
