"""Parameter class for Study find_consensus method."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class find_consensus_defaults:
    """
    Parameter class for Study find_consensus method.

    This class encapsulates parameters for consensus feature detection across samples,
    including algorithm selection, grouping tolerances, and minimum sample requirements.

    Attributes:
        algorithm (str): Feature grouping algorithm. Default is "qt".
        min_samples (int): Minimum number of samples for a consensus feature. Default is 1.
        link_ms2 (bool): Whether to link MS2 spectra to consensus features. Default is True.
        mz_tol (float): m/z tolerance for grouping (Da). Default is 0.01.
        rt_tol (float): RT tolerance for grouping (seconds). Default is 1.0.
    """

    algorithm: str = "qt"
    min_samples: int = 1
    link_ms2: bool = True
    mz_tol: float = 0.01
    rt_tol: float = 1.0

    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "algorithm": {
                "dtype": str,
                "description": "Feature grouping algorithm",
                "default": "qt",
                "allowed_values": ["qt", "kd", "unlabeled", "kd-nowarp"],
            },
            "min_samples": {
                "dtype": int,
                "description": "Minimum number of samples for a consensus feature",
                "default": 1,
                "min_value": 1,
            },
            "link_ms2": {
                "dtype": bool,
                "description": "Whether to link MS2 spectra to consensus features",
                "default": True,
            },
            "mz_tol": {
                "dtype": float,
                "description": "m/z tolerance for grouping (Da)",
                "default": 0.01,
                "min_value": 0.001,
                "max_value": 1.0,
            },
            "rt_tol": {
                "dtype": float,
                "description": "RT tolerance for grouping (seconds)",
                "default": 1.0,
                "min_value": 0.1,
                "max_value": 60.0,
            },
        },
        repr=False,
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
