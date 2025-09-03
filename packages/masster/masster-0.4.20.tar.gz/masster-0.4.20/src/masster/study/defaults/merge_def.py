"""Parameter class for Study merge method."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class merge_defaults:
    """
    Parameter class for Study merge method.

    This class encapsulates parameters for all merge algorithms including
    method selection, grouping tolerances, and algorithm-specific parameters.

    Attributes:
        method (str): Merge method to use ('kd', 'qt', 'kd-nowarp', 'chunked'). Default is "kd".
        min_samples (int): Minimum number of samples for a consensus feature. Default is 50.
        rt_tol (float): RT tolerance for grouping (seconds). Default is 2.0.
        mz_tol (float): m/z tolerance for grouping (Da for all methods). Default is 0.01.
        chunk_size (int): Chunk size for 'chunked' method. Default is 500.
        nr_partitions (int): Number of partitions in m/z dimension for KD algorithms. Default is 500.
        min_rel_cc_size (float): Minimum relative connected component size for conflict resolution. Default is 0.3.
        max_pairwise_log_fc (float): Maximum pairwise log fold change for conflict resolution. Default is 0.5.
        max_nr_conflicts (int): Maximum number of conflicts allowed in consensus feature. Default is 0.
        link_ms2 (bool): Whether to link MS2 spectra to consensus features. Default is True.
    """

    method: str = "qt"
    min_samples: int = 2
    rt_tol: float = 5.0
    mz_tol: float = 0.01
    chunk_size: int = 500
    nr_partitions: int = 1000
    min_rel_cc_size: float = 0.1
    max_pairwise_log_fc: float = -1.0
    max_nr_conflicts: int = 0
    link_ms2: bool = True
    
    # Parallel processing parameters
    threads: Optional[int] = None
    
    # KD-Strict specific parameters
    optimize_rt_tol: bool = False
    rt_tol_range: tuple = (0.5, 4.0)  
    rt_tol_steps: int = 7
    secondary_merge_rt_tol: float = 1.0
    secondary_merge_mz_tol: float = 0.005
    min_sample_overlap: float = 0.8
    max_rt_spread: float = 2.0  # Will default to 2x rt_tol
    min_coherence: float = 0.0

    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "method": {
                "dtype": str,
                "description": "Merge method (algorithm) to use",
                "default": "quality",
                "allowed_values": ["sensitivity", "qt", "nowarp", "chunked", "quality", 
                                 "kd", "kd-nowarp", "kd_nowarp", "kd-strict", "kd_strict",
                                 "kd_chunked", "kd-chunked", "qt_chunked", "qt-chunked"],
            },
            "min_samples": {
                "dtype": int,
                "description": "Minimum number of samples for a consensus feature",
                "default": 50,
                "min_value": 1,
            },
            "rt_tol": {
                "dtype": float,
                "description": "RT tolerance for grouping (seconds)",
                "default": 2.0,
                "min_value": 0.1,
                "max_value": 60.0,
            },
            "mz_tol": {
                "dtype": float,
                "description": "m/z tolerance for grouping (Da for all methods)",
                "default": 0.01,
                "min_value": 0.001,
                "max_value": 1.0,
            },
            "chunk_size": {
                "dtype": int,
                "description": "Chunk size for 'chunked' method",
                "default": 500,
                "min_value": 10,
            },
            "nr_partitions": {
                "dtype": int,
                "description": "Number of partitions in m/z dimension for KD algorithms",
                "default": 500,
                "min_value": 10,
                "max_value": 10000,
            },
            "min_rel_cc_size": {
                "dtype": float,
                "description": "Minimum relative connected component size for conflict resolution",
                "default": 0.3,
                "min_value": 0.0,
                "max_value": 1.0,
            },
            "max_pairwise_log_fc": {
                "dtype": float,
                "description": "Maximum pairwise log fold change for conflict resolution",
                "default": 0.5,
                "min_value": 0.0,
                "max_value": 10.0,
            },
            "max_nr_conflicts": {
                "dtype": int,
                "description": "Maximum number of conflicts allowed in consensus feature",
                "default": 0,
                "min_value": 0,
                "max_value": 1000,
            },
            "link_ms2": {
                "dtype": bool,
                "description": "Whether to link MS2 spectra to consensus features",
                "default": True,
            },
            # Parallel processing parameters
            "threads": {
                "dtype": [int, type(None)],
                "description": "Number of parallel threads/processes for chunked methods (None=original sequential)",
                "default": None,
                "min_value": 1,
                "max_value": 32,
            },
            # KD-Strict specific parameters
            "optimize_rt_tol": {
                "dtype": bool,
                "description": "Enable RT tolerance optimization for kd-strict method",
                "default": False,
            },
            "rt_tol_range": {
                "dtype": tuple,
                "description": "RT tolerance range for optimization (min, max) in seconds",
                "default": (0.8, 2.0),
            },
            "rt_tol_steps": {
                "dtype": int,
                "description": "Number of steps for RT tolerance optimization",
                "default": 5,
                "min_value": 3,
                "max_value": 20,
            },
            "secondary_merge_rt_tol": {
                "dtype": float,
                "description": "RT tolerance for secondary clustering in kd-strict (seconds)",
                "default": 0.5,
                "min_value": 0.1,
                "max_value": 5.0,
            },
            "secondary_merge_mz_tol": {
                "dtype": float,
                "description": "m/z tolerance for secondary clustering in kd-strict (Da)",
                "default": 0.005,
                "min_value": 0.001,
                "max_value": 0.1,
            },
            "min_sample_overlap": {
                "dtype": float,
                "description": "Minimum sample overlap ratio for merging features (0.0-1.0)",
                "default": 0.8,
                "min_value": 0.0,
                "max_value": 1.0,
            },
            "max_rt_spread": {
                "dtype": float,
                "description": "Maximum allowed RT spread in seconds (None = 3x rt_tol)",
                "default": None,
                "min_value": 0.1,
            },
            "min_coherence": {
                "dtype": float,
                "description": "Minimum chromatographic coherence score (0.0 = disabled)",
                "default": 0.0,
                "min_value": 0.0,
                "max_value": 1.0,
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

        # Handle Optional types (list of types including None)
        if isinstance(expected_dtype, list):
            # Check if value matches any of the allowed types
            valid_type = False
            for dtype in expected_dtype:
                if dtype is type(None) and value is None:
                    return True  # None is explicitly allowed
                elif dtype is int and isinstance(value, int):
                    valid_type = True
                    break
                elif dtype is float and isinstance(value, (int, float)):
                    valid_type = True
                    break
                elif dtype is bool and isinstance(value, bool):
                    valid_type = True
                    break
                elif dtype is str and isinstance(value, str):
                    valid_type = True
                    break
            
            if not valid_type:
                return False
            
            # For None values, skip further validation
            if value is None:
                return True
            
            # Use the first non-None type for range validation
            expected_dtype = next((dt for dt in expected_dtype if dt is not type(None)), expected_dtype[0])

        # Type checking for non-Optional types
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
