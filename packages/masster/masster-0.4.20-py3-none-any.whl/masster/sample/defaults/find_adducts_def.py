"""
Find Adducts Parameters Module

This module defines parameters for adduct detection in mass spectrometry data.
It consolidates all parameters used in the find_adducts() method with type checking,
validation, and comprehensive descriptions.

Classes:
    find_adducts_defaults: Configuration parameters for the find_adducts() method.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class find_adducts_defaults:
    """
    Parameters for mass spectrometry adduct detection using OpenMS MetaboliteFeatureDeconvolution.

    This class consolidates all parameters used in the find_adducts() method including
    potential adducts, charge constraints, and retention time tolerances.
    It provides type checking, validation, and comprehensive parameter descriptions.

    Adduct Detection Parameters:
        adducts: List of potential adducts or ionization mode string.
        charge_min: Minimal possible charge state.
        charge_max: Maximal possible charge state.
        charge_span_max: Maximum span between different charge states.
        retention_max_diff: Maximum retention time difference for adduct grouping.
        retention_max_diff_local: Maximum local retention time difference.

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
        - get_openms_adducts(): Get processed adducts list for OpenMS
    """

    # Adduct specification
    adducts: list[str] | str | None = None

    # Charge constraints
    charge_min: int = 1
    charge_max: int = 2
    charge_span_max: int = 2

    # Retention time constraints (in seconds - final confirmed unit)
    retention_max_diff: float = 1.0  # 1 second - precise RT grouping
    retention_max_diff_local: float = 1.0  # 1 second - precise RT grouping

    # Mass tolerance constraints
    mass_max_diff: float = (
        0.01  # 0.01 Da - strict mass tolerance for chemical specificity
    )
    unit: str = "Da"  # Mass tolerance unit: "Da" or "ppm"

    # Probability filtering
    min_probability: float = 0.03  # Minimum probability to consider adducts (filters low-probability adducts)

    # Parameter metadata for validation and description
    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "adducts": {
                "dtype": "Union[List[str], str, None]",
                "description": "List of potential adducts or ionization mode ('pos', 'neg', 'positive', 'negative')",
                "allowed_values": ["pos", "neg", "positive", "negative"],
            },
            "charge_min": {
                "dtype": int,
                "description": "Minimal possible charge state for adduct detection",
                "min_value": 1,
                "max_value": 10,
            },
            "charge_max": {
                "dtype": int,
                "description": "Maximal possible charge state for adduct detection",
                "min_value": 1,
                "max_value": 10,
            },
            "charge_span_max": {
                "dtype": int,
                "description": "Maximum span between different charge states in the same adduct group",
                "min_value": 1,
                "max_value": 5,
            },
            "retention_max_diff": {
                "dtype": float,
                "description": "Maximum retention time difference (in seconds) for global adduct grouping",
                "min_value": 0.05,
                "max_value": 120.0,  # 2 minutes max seems reasonable
            },
            "retention_max_diff_local": {
                "dtype": float,
                "description": "Maximum local retention time difference (in seconds) for adduct grouping",
                "min_value": 0.05,
                "max_value": 120.0,  # 2 minutes max seems reasonable
            },
            "mass_max_diff": {
                "dtype": float,
                "description": "Maximum mass tolerance for feature grouping (symmetric window around each feature)",
                "min_value": 0.001,
                "max_value": 1.0,
            },
            "unit": {
                "dtype": str,
                "description": "Unit for mass tolerance: 'Da' or 'ppm'",
                "allowed_values": ["Da", "ppm"],
            },
            "min_probability": {
                "dtype": float,
                "description": "Minimum probability threshold to consider adducts (filters out low-probability adduct combinations)",
                "min_value": 0.0,
                "max_value": 1.0,
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

        # Handle Union types for adducts parameter
        if param_name == "adducts":
            if value is None:
                return True
            if isinstance(value, str):
                # Check if it's a valid ionization mode
                allowed_values = metadata.get("allowed_values", [])
                return value in allowed_values
            elif isinstance(value, list):
                # Check if all elements are strings
                return all(isinstance(item, str) for item in value)
            else:
                return False

        # Handle unit parameter
        if param_name == "unit":
            if isinstance(value, str):
                allowed_values = metadata.get("allowed_values", [])
                return value in allowed_values
            else:
                return False

        # Type checking for non-Union types
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

        # Range validation for numeric types
        if expected_dtype in (int, float):
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
            if expected_dtype is int and not isinstance(value, int):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    if validate:
                        return False
            elif expected_dtype is float and not isinstance(value, float):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    if validate:
                        return False

        setattr(self, param_name, value)

        # Trigger dynamic calculation if this is the adducts parameter
        if param_name == "adducts":
            self._update_openms_adducts()

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

    def _update_openms_adducts(self) -> None:
        """
        Update the internal OpenMS adducts list when adducts parameter changes.
        This is called automatically when the adducts parameter is set.
        """
        # This will update the internal state that get_openms_adducts() uses
        pass

    def get_openms_adducts(self) -> list[str]:
        """
        Get the processed adducts list for OpenMS MetaboliteFeatureDeconvolution.

        Returns:
            List of adduct strings formatted for OpenMS
        """
        adducts = self.adducts

        if adducts is None or adducts in ["pos", "positive"]:
            return [
                "+H:1:0.65",
                "+Na:1:0.15",
                "+NH4:1:0.15",
                "+K:1:0.05",
                "-H2O:0:0.15",
            ]
        elif adducts in ["neg", "negative"]:
            return [
                "-H:-1:0.9",
                "+Cl:-1:0.1",
                "+CH2O2:0:0.15",
                "-H2O:0:0.15",
            ]
        elif isinstance(adducts, list):
            return adducts
        else:
            # Fallback to positive mode if unexpected format
            return [
                "+H:1:0.65",
                "+Na:1:0.15",
                "+NH4:1:0.15",
                "+K:1:0.05",
                "-H2O:0:0.2",
            ]
