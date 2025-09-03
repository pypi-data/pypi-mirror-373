"""
Find Features Parameters Module

This module defines parameters for feature detection in mass spectrometry data.
It consolidates all parameters used in the find_features() method with type checking,
validation, and comprehensive descriptions.

Classes:
    find_features_defaults: Configuration parameters for the find_features() method.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class find_features_defaults:
    """Configuration defaults for the feature-finding pipeline.

    This dataclass centralizes parameters used by the `find_features()` routine
    (mass-trace detection, elution-peak detection and feature assembly).  The
    purpose of this docstring is to explain the role and impact of the main
    parameters users commonly tune.

    Main parameters (what they mean, units and guidance):

    - chrom_fwhm (float, seconds):
        Expected chromatographic peak full-width at half-maximum (FWHM) in
        seconds. This value informs the peak detection algorithms about the
        typical temporal width of chromatographic peaks. It is used for
        smoothing, window sizes when searching for local maxima and when
        calculating RT-based tolerances. Use a value that matches your LC
        method: smaller values for sharp, fast chromatography and larger values
        for broader peaks. Default: 1.0 s.

    - noise (float, intensity units):
        Intensity threshold used to filter out low-intensity signals before
        mass-trace and peak detection. Points with intensity below this
        threshold are treated as background and typically ignored. Raising
        `noise` reduces false positives from background fluctuations but may
        remove low-abundance true peaks; lowering it increases sensitivity at
        the cost of more noise. Default: 200.0 (instrument-dependent).

    - chrom_peak_snr (float, unitless):
        Minimum signal-to-noise ratio required to accept a detected
        chromatographic peak. SNR is typically computed as peak height
        (or crest intensity) divided by an estimate of local noise. A higher
        `chrom_peak_snr` makes detection stricter (fewer false positives),
        while a lower value makes detection more permissive (more low-SNR
        peaks accepted). Typical values range from ~3 (relaxed) to >10
        (stringent). Default: 10.0.

    - isotope_filtering_model (str):
        Isotope filtering model to use ('metabolites (2% RMS)', 'metabolites (5% RMS)',
        'peptides', 'none'). Default: 'metabolites (5% RMS)'.

    Use these three parameters together to balance sensitivity and
    specificity for your dataset: tune `chrom_fwhm` to match chromatographic
    peak shapes, set `noise` to a conservative background level for your
    instrument, then adjust `chrom_peak_snr` to control how aggressively
    peaks are accepted or rejected.

    The class also contains many other configuration options (mass tolerances,
    isotope handling, post-processing and reporting flags). See individual
    parameter metadata (`_param_metadata`) for allowed ranges and types.
    """

    # Main params
    noise: float = 200.0
    chrom_fwhm: float = 1.0
    chrom_peak_snr: float = 10.0

    # Mass Trace Detection parameters
    tol_ppm: float = 30.0
    reestimate_mt_sd: bool = True
    quant_method: str = "area"
    trace_termination_criterion: str = "outlier"
    trace_termination_outliers: int = 5
    min_sample_rate: float = 0.5

    min_trace_length: float = 0.5
    min_trace_length_multiplier: float = 0.2
    max_trace_length: float = -1.0

    # Elution Peak Detection parameters
    enabled: bool = True
    chrom_fwhm_min: float = 0.2
    chrom_fwhm_max: float = 60.0
    width_filtering: str = "fixed"
    masstrace_snr_filtering: bool = False

    # Feature Finding parameters
    local_rt_range: float = 1.0
    local_mz_range: float = 5.0
    charge_lower_bound: int = 0
    charge_upper_bound: int = 5

    report_smoothed_intensities: bool = False
    remove_single_traces: bool = False
    report_convex_hulls: bool = True
    report_summed_ints: bool = False
    report_chromatograms: bool = True
    mz_scoring_13C: bool = False

    threads: int = 1
    no_progress: bool = False
    debug: bool = False

    # Post-processing parameters
    deisotope: bool = True
    deisotope_mz_tol: float = 0.02
    deisotope_rt_tol_factor: float = 0.5  # Will be multiplied by chrom_fwhm
    isotope_filtering_model: str = "metabolites (5% RMS)"

    # chrom extraction parameters

    # Parameter metadata for validation and description
    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "tol_ppm": {
                "dtype": float,
                "description": "Mass error tolerance in parts-per-million for mass trace detection",
                "min_value": 0.1,
                "max_value": 100.0,
            },
            "noise": {
                "dtype": float,
                "description": "VIP: Noise threshold intensity to filter out low-intensity signals",
                "min_value": 0.0,
                "max_value": float("inf"),
            },
            "min_trace_length_multiplier": {
                "dtype": float,
                "description": "Multiplier for minimum trace length calculation (multiplied by chrom_fwhm_min)",
                "min_value": 0.1,
                "max_value": 2.0,
            },
            "trace_termination_outliers": {
                "dtype": int,
                "description": "Number of outliers allowed before terminating a mass trace",
                "min_value": 1,
                "max_value": 10,
            },
            "chrom_fwhm": {
                "dtype": float,
                "description": "VIP: Full width at half maximum for chromatographic peak shape in elution peak detection",
                "min_value": 0.1,
                "max_value": 30.0,
            },
            "chrom_fwhm_min": {
                "dtype": float,
                "description": "Minimum FWHM for chromatographic peak detection",
                "min_value": 0.1,
                "max_value": 5.0,
            },
            "chrom_peak_snr": {
                "dtype": float,
                "description": "VIP: Signal-to-noise ratio required for chromatographic peaks",
                "min_value": 1.0,
                "max_value": 100.0,
            },
            "masstrace_snr_filtering": {
                "dtype": bool,
                "description": "Whether to apply signal-to-noise filtering to mass traces",
            },
            "mz_scoring_13C": {
                "dtype": bool,
                "description": "Whether to enable scoring of 13C isotopic patterns during peak detection",
            },
            "width_filtering": {
                "dtype": str,
                "description": "Width filtering method for mass traces",
                "allowed_values": ["fixed", "auto"],
            },
            "remove_single_traces": {
                "dtype": bool,
                "description": "Whether to remove mass traces without satellite isotopic traces",
            },
            "report_convex_hulls": {
                "dtype": bool,
                "description": "Whether to report convex hulls for detected features",
            },
            "report_summed_ints": {
                "dtype": bool,
                "description": "Whether to report summed intensities for features",
            },
            "report_chromatograms": {
                "dtype": bool,
                "description": "Whether to report chromatograms for features",
            },
            "deisotope": {
                "dtype": bool,
                "description": "Whether to perform deisotoping of detected features to remove redundant isotope peaks",
            },
            "deisotope_mz_tol": {
                "dtype": float,
                "description": "m/z tolerance for deisotoping (Da)",
                "min_value": 0.001,
                "max_value": 0.1,
            },
            "deisotope_rt_tol_factor": {
                "dtype": float,
                "description": "RT tolerance factor for deisotoping (multiplied by chrom_fwhm_min/4)",
                "min_value": 0.1,
                "max_value": 2.0,
            },
            "isotope_filtering_model": {
                "dtype": str,
                "description": "Isotope filtering model",
                "default": "metabolites (5% RMS)",
                "allowed_values": ["metabolites (2% RMS)", "metabolites (5% RMS)", "peptides", "none"],
            },
            "threads": {
                "dtype": int,
                "description": "Number of threads to use for parallel processing",
                "min_value": 1,
                "max_value": 64,
            },
            "no_progress": {
                "dtype": bool,
                "description": "Disable progress logging",
            },
            "debug": {
                "dtype": bool,
                "description": "Enable debug mode for detailed logging",
            },
            "min_sample_rate": {
                "dtype": float,
                "description": "Minimum sample rate for mass trace detection",
                "min_value": 0.1,
                "max_value": 1.0,
            },
            "min_trace_length": {
                "dtype": int,
                "description": "Minimum trace length in number of spectra",
                "min_value": 2,
                "max_value": 100,
            },
            """            "min_fwhm": {
                "dtype": float,
                "description": "Minimum full width at half maximum for peaks (seconds)",
                "min_value": 0.1,
                "max_value": 10.0,
            },"""
            "chrom_fwhm_max": {
                "dtype": float,
                "description": "Maximum full width at half maximum for peaks (seconds)",
                "min_value": 1.0,
                "max_value": 300.0,
            },
            "trace_termination_criterion": {
                "dtype": str,
                "description": "Criterion for mass trace termination",
                "allowed_values": ["outlier", "sample_rate"],
            },
            "reestimate_mt_sd": {
                "dtype": bool,
                "description": "Whether to re-estimate mass trace standard deviation",
            },
            "quant_method": {
                "dtype": str,
                "description": "Quantification method for features",
                "allowed_values": ["area", "height"],
            },
            "enabled": {
                "dtype": bool,
                "description": "Whether elution peak detection is enabled",
            },
            "local_rt_range": {
                "dtype": float,
                "description": "Local retention time range for feature finding (seconds)",
                "min_value": 1.0,
                "max_value": 100.0,
            },
            "local_mz_range": {
                "dtype": float,
                "description": "Local m/z range for feature finding (Da)",
                "min_value": 1.0,
                "max_value": 20.0,
            },
            "charge_lower_bound": {
                "dtype": int,
                "description": "Lower bound for charge state detection",
                "min_value": 1,
                "max_value": 10,
            },
            "charge_upper_bound": {
                "dtype": int,
                "description": "Upper bound for charge state detection",
                "min_value": 1,
                "max_value": 10,
            },
            "report_smoothed_intensities": {
                "dtype": bool,
                "description": "Whether to report smoothed intensities for features",
            },
        },
    )

    def get_info(self, param_name: str) -> dict[str, Any]:
        """
        Get information about a specific parameter.

        Args:
            param_name: Name of the parameter

        Returns:
            Dictionary containing parameter metadata

        Raises:
            KeyError: If parameter name is not found
        """
        if param_name not in self._param_metadata:
            raise KeyError(f"Parameter '{param_name}' not found")
        return self._param_metadata[param_name]

    def get_description(self, param_name: str) -> str:
        """
        Get description for a specific parameter.

        Args:
            param_name: Name of the parameter

        Returns:
            Parameter description string
        """
        return str(self.get_info(param_name)["description"])

    def validate(self, param_name: str, value: Any) -> bool:
        """
        Validate a parameter value against its constraints.

        Args:
            param_name: Name of the parameter
            value: Value to validate

        Returns:
            True if value is valid, False otherwise
        """
        if param_name not in self._param_metadata:
            return False

        metadata = self._param_metadata[param_name]
        expected_dtype = metadata["dtype"]

        # Check type
        if not isinstance(value, expected_dtype):
            try:
                # Try to convert to expected type
                value = expected_dtype(value)
            except (ValueError, TypeError):
                return False

        # Check range constraints for numeric types
        if expected_dtype in (int, float):
            if "min_value" in metadata and value < metadata["min_value"]:
                return False
            if "max_value" in metadata and value > metadata["max_value"]:
                return False

        # Check allowed values for strings
        if expected_dtype is str and "allowed_values" in metadata:
            if value not in metadata["allowed_values"]:
                return False

        return True

    def set(self, param_name: str, value: Any, validate: bool = True) -> bool:
        """
        Set a parameter value with optional validation.

        Args:
            param_name: Name of the parameter
            value: New value for the parameter
            validate: Whether to validate the value before setting

        Returns:
            True if parameter was set successfully, False otherwise
        """
        if not hasattr(self, param_name):
            return False

        if validate and not self.validate(param_name, value):
            return False

        # Convert to expected type if needed
        if param_name in self._param_metadata:
            expected_dtype = self._param_metadata[param_name]["dtype"]
            try:
                value = expected_dtype(value)
            except (ValueError, TypeError):
                if validate:
                    return False

        setattr(self, param_name, value)
        return True

    def get(self, param_name: str) -> Any:
        """
        Get the value of a parameter by name.
        Args:
            param_name: Name of the parameter
        Returns:
            Current value of the parameter
        """
        if not hasattr(self, param_name):
            raise KeyError(f"Parameter '{param_name}' not found")
        return getattr(self, param_name)

    def set_from_dict(
        self,
        param_dict: dict[str, Any],
        validate: bool = True,
    ) -> list[str]:
        """
        Update multiple parameters from a dictionary.

        Args:
            param_dict: Dictionary of parameter names and values
            validate: Whether to validate values before setting

        Returns:
            List of parameter names that could not be set
        """
        failed_params = []

        for param_name, value in param_dict.items():
            if not self.set(param_name, value, validate):
                failed_params.append(param_name)

        return failed_params

    def to_dict(self) -> dict[str, Any]:
        """
        Convert parameters to dictionary, excluding metadata.

        Returns:
            Dictionary of parameter names and values
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def list_parameters(self) -> list[str]:
        """
        Get list of all parameter names.

        Returns:
            List of parameter names
        """
        return [k for k in self.__dict__.keys() if not k.startswith("_")]

    def validate_all(self) -> tuple[bool, list[str]]:
        """
        Validate all parameters in the instance.

        Returns:
            Tuple of (all_valid, list_of_invalid_params)
            - all_valid: True if all parameters are valid, False otherwise
            - list_of_invalid_params: List of parameter names that failed validation
        """
        invalid_params = []

        for param_name in self.list_parameters():
            if param_name in self._param_metadata:
                current_value = getattr(self, param_name)
                if not self.validate(param_name, current_value):
                    invalid_params.append(param_name)

        return len(invalid_params) == 0, invalid_params
