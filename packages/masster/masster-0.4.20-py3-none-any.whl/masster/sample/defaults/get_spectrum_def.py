"""
Get Spectrum Parameters Module

This module defines parameters for spectrum retrieval and processing in mass spectrometry data.
It consolidates all parameters used in the get_spectrum() method with type checking,
validation, and comprehensive descriptions.

Classes:
    get_spectrum_defaults: Configuration parameters for the get_spectrum() method.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class get_spectrum_defaults:
    """
    Parameters for spectrum retrieval and processing.

    This class consolidates all parameters used in the get_spectrum() method including
    scan identification, spectrum processing options, and optional parameters.
    It provides type checking, validation, and comprehensive parameter descriptions.

    Spectrum Processing Parameters:
        scan: Unique identifier of the scan to retrieve.
        precursor_trim: Value used to trim the precursor m/z for MS2 spectra.
        max_peaks: Maximum number of peaks to retain in the spectrum.
        centroid: Flag indicating whether the spectrum should be centroided.
        deisotope: Flag indicating whether deisotoping should be performed.
        dia_stats: Flag for processing DIA (data-independent acquisition) statistics.
        feature: An optional identifier used when computing DIA statistics.
        label: Optional label to assign to the spectrum.
        centroid_algo: Algorithm to use for centroiding.

    Available Methods:
        - validate(param_name, value): Validate a single parameter value
        - validate_all(): Validate all parameters at once
        - to_dict(): Convert parameters to dictionary
        - set_from_dict(param_dict, validate=True): Update multiple parameters from dict
        - set(param_name, value, validate=True): Set parameter value with validation
        - get(param_name): Get parameter value
        - get_description(param_name): Get parameter description
        - get_info(param_name): Get full parameter metadata
        - list_parameters(): Get list of all parameter names
    """

    scan: list[int] = field(default_factory=lambda: [0])
    precursor_trim: int = -10
    max_peaks: int | None = 50000
    centroid: bool = True
    deisotope: bool = True
    dia_stats: bool | None = False
    feature: int | None = None
    label: str | None = None
    centroid_algo: str | None = "lmp"

    # Parameter metadata for validation and description
    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "scan": {
                "dtype": list,
                "description": "List of scan identifiers to retrieve",
            },
            "precursor_trim": {
                "dtype": int,
                "description": "Value used to trim the precursor m/z for MS2 spectra",
                "min_value": -50,
                "max_value": 50,
            },
            "max_peaks": {
                "dtype": "Optional[int]",
                "description": "Maximum number of peaks to retain in the spectrum",
                "min_value": 1,
                "max_value": 100000,
            },
            "centroid": {
                "dtype": bool,
                "description": "Flag indicating whether the spectrum should be centroided",
            },
            "deisotope": {
                "dtype": bool,
                "description": "Flag indicating whether deisotoping should be performed",
            },
            "dia_stats": {
                "dtype": "Optional[bool]",
                "description": "Flag for processing DIA (data-independent acquisition) statistics",
            },
            "feature": {
                "dtype": "Optional[int]",
                "description": "An optional identifier used when computing DIA statistics",
            },
            "label": {
                "dtype": "Optional[str]",
                "description": "Optional label to assign to the spectrum",
            },
            "centroid_algo": {
                "dtype": "Optional[str]",
                "description": "Algorithm to use for centroiding",
                "allowed_values": ["lmp", "cwt", "gaussian"],
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

        # Handle optional types
        if isinstance(expected_dtype, str) and expected_dtype.startswith("Optional"):
            if value is None:
                return True
            # Extract the inner type for validation
            if "int" in expected_dtype:
                expected_dtype = int
            elif "str" in expected_dtype:
                expected_dtype = str
            elif "bool" in expected_dtype:
                expected_dtype = bool

        # Type checking
        if expected_dtype is int:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    return False
        elif expected_dtype is float:
            if not isinstance(value, (int, float)):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    return False
        elif expected_dtype is bool:
            if not isinstance(value, bool):
                return False
        elif expected_dtype is str:
            if not isinstance(value, str):
                return False
        elif expected_dtype is list:
            if not isinstance(value, list):
                return False

        # Range validation for numeric types
        if expected_dtype in (int, float) and isinstance(value, (int, float)):
            if "min_value" in metadata and value < metadata["min_value"]:
                return False
            if "max_value" in metadata and value > metadata["max_value"]:
                return False

        # Allowed values validation for strings
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

            # Handle optional types
            if isinstance(expected_dtype, str) and expected_dtype.startswith("Optional") and value is not None:
                if "int" in expected_dtype and not isinstance(value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        if validate:
                            return False
                elif "float" in expected_dtype and not isinstance(value, float):
                    try:
                        value = float(value)
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
