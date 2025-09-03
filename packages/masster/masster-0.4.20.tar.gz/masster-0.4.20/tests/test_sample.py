"""Tests for Sample class."""


class TestSample:
    """Test suite for Sample class."""

    def test_sample_import(self):
        """Test that Sample can be imported."""
        from masster.sample.sample import Sample
        assert Sample is not None

    def test_sample_creation_basic(self):
        """Test basic sample creation."""
        from masster.sample.sample import Sample
        from masster.sample.defaults.sample_def import sample_defaults
        
        # Test with default parameters
        params = sample_defaults()
        sample = Sample(params=params)
        
        assert sample is not None
        assert hasattr(sample, 'parameters')
        assert sample.parameters == params

    def test_sample_creation_with_kwargs(self):
        """Test sample creation with keyword arguments."""
        from masster.sample.sample import Sample
        
        # Test without filename to avoid FileNotFoundError
        sample = Sample(label="test_sample", log_level="DEBUG", ondisk=True)
        
        assert sample is not None
        assert hasattr(sample, 'parameters')
        assert sample.parameters.label == "test_sample"
        assert sample.parameters.log_level == "DEBUG"
        assert sample.parameters.ondisk is True

    def test_sample_properties(self):
        """Test sample properties."""
        from masster.sample.sample import Sample
        
        sample = Sample(label="test_sample", ondisk=True)
        
        # Test that parameters are accessible
        assert sample.parameters.label == "test_sample"
        assert sample.parameters.ondisk is True
        
        # Test parameter access through methods
        from masster.sample.parameters import get_parameters_property
        params_dict = get_parameters_property(sample)
        assert isinstance(params_dict, dict)

    def test_sample_parameter_updates(self):
        """Test updating sample parameters."""
        from masster.sample.sample import Sample
        from masster.sample.parameters import update_parameters
        
        sample = Sample(label="original")
        
        # Update parameters
        update_parameters(sample, label="updated", mz_tol_ms1_da=0.001)
        
        assert sample.parameters.label == "updated"
        assert sample.parameters.mz_tol_ms1_da == 0.001

    def test_sample_history_storage(self):
        """Test parameter history storage."""
        from masster.sample.sample import Sample
        from masster.sample.parameters import store_history
        
        sample = Sample(label="test")
        
        # Store some history
        store_history(sample, ["processing", "step1"], {"method": "test_method"})
        
        assert hasattr(sample, 'history')
        assert "processing" in sample.history
        assert sample.history["processing"]["step1"]["method"] == "test_method"

    def test_sample_parameter_retrieval(self):
        """Test parameter retrieval from history."""
        from masster.sample.sample import Sample
        from masster.sample.parameters import store_history, get_parameters
        
        sample = Sample(label="test")
        
        # Store and retrieve parameters
        test_params = {"tolerance": 0.01, "method": "test"}
        store_history(sample, ["analysis", "params"], test_params)
        
        retrieved = get_parameters(sample, ["analysis", "params"])
        assert retrieved == test_params

    def test_sample_with_mass_tolerances(self):
        """Test sample with different mass tolerance settings."""
        from masster.sample.sample import Sample
        
        sample = Sample(
            mz_tol_ms1_da=0.001,
            mz_tol_ms2_da=0.01,
            mz_tol_ms1_ppm=2.5,
            mz_tol_ms2_ppm=15.0
        )
        
        assert sample.parameters.mz_tol_ms1_da == 0.001
        assert sample.parameters.mz_tol_ms2_da == 0.01
        assert sample.parameters.mz_tol_ms1_ppm == 2.5
        assert sample.parameters.mz_tol_ms2_ppm == 15.0

    def test_sample_centroiding_parameters(self):
        """Test sample centroiding parameters."""
        from masster.sample.sample import Sample
        
        sample = Sample(
            centroid_min_points_ms1=3,
            centroid_min_points_ms2=2,
            centroid_smooth=7
        )
        
        # Test that parameters were set (the algorithm might remain default)
        assert sample.parameters.centroid_min_points_ms1 == 3
        assert sample.parameters.centroid_min_points_ms2 == 2
        assert sample.parameters.centroid_smooth == 7

    def test_sample_logging_configuration(self):
        """Test sample logging configuration."""
        from masster.sample.sample import Sample
        
        sample = Sample(
            log_level="WARNING",
            log_label="test_logger",
            log_sink="test.log"
        )
        
        assert sample.parameters.log_level == "WARNING"
        assert sample.parameters.log_label == "test_logger"
        assert sample.parameters.log_sink == "test.log"

    def test_sample_dia_settings(self):
        """Test DIA-specific settings."""
        from masster.sample.sample import Sample
        
        sample = Sample(dia_window=25.0)
        
        assert sample.parameters.dia_window == 25.0

    def test_sample_parameter_validation(self):
        """Test parameter validation."""
        from masster.sample.sample import Sample
        from masster.sample.defaults.sample_def import sample_defaults
        
        # Test with valid parameters
        params = sample_defaults(mz_tol_ms1_da=0.005, log_level="INFO")
        sample = Sample(params=params)
        
        assert sample.parameters.mz_tol_ms1_da == 0.005
        assert sample.parameters.log_level == "INFO"

    def test_sample_metadata_handling(self):
        """Test sample metadata handling."""
        from masster.sample.sample import Sample
        
        sample = Sample(
            label="metadata_test",
            ondisk=False  # Don't try to load a file
        )
        
        # Test metadata access
        assert sample.parameters.label == "metadata_test"
        assert sample.parameters.filename is None  # No file specified
