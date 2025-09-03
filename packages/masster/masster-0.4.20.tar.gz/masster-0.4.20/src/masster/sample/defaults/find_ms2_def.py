"""
Find MS2 Parameters Module

This module defines parameters for MS2 spectrum linking in mass spectrometry data.
It consolidates all parameters used in the find_ms2() method with type checking,
validation, and comprehensive descriptions.

Classes:
    find_ms2_defaults: Configuration parameters for the find_ms2() method.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class find_ms2_defaults:
    """
    Parameters for MS2 spectrum linking functionality.

    This class consolidates all parameters used in the find_ms2() method including
    m/z tolerance, centroiding options, and processing flags.
    It provides type checking, validation, and comprehensive parameter descriptions.

    MS2 Linking Parameters:
        mz_tol: m/z tolerance for MS2 precursor matching.
        centroid: Whether to centroid the returned spectrum.
        deisotope: Whether to deisotope the returned spectrum.
        dia_stats: Whether to collect DIA-related statistics.
        features: Specific feature UID(s) to process, or None for all.
        mz_tol_ztscan: m/z tolerance for ztscan/DIA file types.

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
        - get_mz_tolerance(file_type): Get appropriate m/z tolerance based on file type
    """

    # Core MS2 linking parameters
    mz_tol: float = 0.5
    centroid: bool = True
    deisotope: bool = False
    dia_stats: bool = False

    # Feature selection parameters - can be None, int, or list of ints
    features: int | list[int] | None = field(default_factory=list)

    # File type specific adjustments
    mz_tol_ztscan: float = 4.0

    # Parameter metadata for validation and description
    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "mz_tol": {
                "dtype": float,
                "description": "m/z tolerance for MS2 precursor matching",
                "min_value": 0.01,
                "max_value": 10.0,
            },
            "centroid": {
                "dtype": bool,
                "description": "Whether to centroid the returned spectrum",
            },
            "deisotope": {
                "dtype": bool,
                "description": "Whether to deisotope the returned spectrum",
            },
            "dia_stats": {
                "dtype": bool,
                "description": "Whether to collect DIA-related statistics",
            },
            "features": {
                "dtype": "Union[int, List[int], None]",
                "description": "Specific feature UID(s) to process, or None for all",
            },
            "mz_tol_ztscan": {
                "dtype": float,
                "description": "m/z tolerance for ztscan/DIA file types",
                "min_value": 0.1,
                "max_value": 20.0,
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

        # Handle Union types for features parameter
        if param_name == "features":
            if value is None or isinstance(value, (int, list)):
                if isinstance(value, list):
                    return all(isinstance(item, int) for item in value)
                return True
            return False

        # Type checking for non-Union types
        if expected_dtype is float:
            if not isinstance(value, (int, float)):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    return False
        elif expected_dtype is bool:
            if not isinstance(value, bool):
                return False

        # Range checking for numeric values
        if isinstance(value, (int, float)) and value is not None:
            if "min_value" in metadata and value < metadata["min_value"]:
                return False
            if "max_value" in metadata and value > metadata["max_value"]:
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
            if expected_dtype is float and not isinstance(value, float):
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

    def get_mz_tolerance(self, file_type=None):
        """
        Get the appropriate m/z tolerance based on file type.

        Args:
            file_type (str, optional): File type ('ztscan', 'dia', or other)

        Returns:
            float: Appropriate m/z tolerance value
        """
        if file_type is not None and file_type.lower() in ["ztscan", "dia"]:
            return self.get("mz_tol_ztscan")
        return self.get("mz_tol")
