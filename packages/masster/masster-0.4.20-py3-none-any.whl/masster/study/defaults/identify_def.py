"""Parameter class for Study identify method."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class identify_defaults:
    """
    Parameter class for Study identify method.

    This class encapsulates parameters for consensus feature identification against
    a compound library, including matching tolerances and scoring penalties.

    Attributes:
        mz_tol (float): m/z tolerance for matching (Da). Default is 0.01.
        rt_tol (Optional[float]): RT tolerance for matching (min). Default is None.
        heteroatom_penalty (float): Score penalty for formulas containing heteroatoms (Cl, Br, F, I). Default is 0.7.
        multiple_formulas_penalty (float): Score penalty when multiple formulas match a feature. Default is 0.8.
        multiple_compounds_penalty (float): Score penalty when multiple compounds match a feature. Default is 0.8.
        heteroatoms (list[str]): List of heteroatoms to apply penalty for. Default is ["Cl", "Br", "F", "I"].
    """

    mz_tol: float = 0.01
    rt_tol: Optional[float] = 2.0
    heteroatom_penalty: float = 0.7
    multiple_formulas_penalty: float = 0.8
    multiple_compounds_penalty: float = 0.8
    heteroatoms: list[str] = field(default_factory=lambda: ["Cl", "Br", "F", "I"])

    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "mz_tol": {
                "dtype": float,
                "description": "m/z tolerance for matching (Da)",
                "default": 0.01,
                "min_value": 0.001,
                "max_value": 1.0,
            },
            "rt_tol": {
                "dtype": (float, type(None)),
                "description": "RT tolerance for matching (min). None to disable RT filtering",
                "default": 2.0,
                "min_value": 0.1,
                "max_value": 10.0,
            },
            "heteroatom_penalty": {
                "dtype": float,
                "description": "Score penalty multiplier for formulas containing heteroatoms (Cl, Br, F, I)",
                "default": 0.7,
                "min_value": 0.0,
                "max_value": 1.0,
            },
            "multiple_formulas_penalty": {
                "dtype": float,
                "description": "Score penalty multiplier when multiple formulas match a consensus feature",
                "default": 0.8,
                "min_value": 0.0,
                "max_value": 1.0,
            },
            "multiple_compounds_penalty": {
                "dtype": float,
                "description": "Score penalty multiplier when multiple compounds match a consensus feature",
                "default": 0.8,
                "min_value": 0.0,
                "max_value": 1.0,
            },
            "heteroatoms": {
                "dtype": list,
                "description": "List of heteroatom symbols to apply penalty for",
                "default": ["Cl", "Br", "F", "I"],
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

        # Type checking for rt_tol which can be float or None
        if param_name == "rt_tol":
            if value is not None:
                if not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        return False
                # Range validation for rt_tol when not None
                if "min_value" in metadata and value < metadata["min_value"]:
                    return False
                if "max_value" in metadata and value > metadata["max_value"]:
                    return False
            return True

        # Type checking for other types
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
            # For heteroatoms, ensure all elements are strings
            if param_name == "heteroatoms" and not all(
                isinstance(item, str) for item in value
            ):
                return False

        # Range validation for numeric types
        if expected_dtype in (int, float) and isinstance(value, (int, float)):
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
            metadata = self._param_metadata[param_name]
            expected_dtype = metadata["dtype"]

            if param_name == "rt_tol" and value is not None:
                # Convert rt_tol to float if it's not None
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    if validate:
                        return False
            elif expected_dtype is int and not isinstance(value, int):
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
