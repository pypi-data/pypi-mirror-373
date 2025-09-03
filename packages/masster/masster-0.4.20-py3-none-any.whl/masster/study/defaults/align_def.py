"""Parameter class for Study align method."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class align_defaults:
    """
    Parameter class for Study align method.

    This class encapsulates parameters for feature alignment across samples,
    including retention time and m/z tolerances, warping parameters, and
    alignment algorithm settings.

    Attributes:
        algorithm (str): Alignment algorithm ('pc' for PoseClustering, 'kd' for KD). Default is 'pc'.
        rt_tol (float): Maximum retention time difference for alignment. Default is 60.0.
        mz_max_diff (float): Maximum m/z difference for alignment. Default is 0.02.
        rt_pair_distance_frac (float): Fraction of RT difference for pair distance. Default is 0.2.
        mz_pair_max_distance (float): Maximum m/z pair distance. Default is 0.01.
        num_used_points (int): Number of points used for alignment. Default is 1000.
        save_features (bool): Whether to save features after alignment. Default is False.
        skip_blanks (bool): Whether to skip blank samples. Default is False.

        KD algorithm specific parameters:
        min_samples (int): Minimum number of samples required for KD alignment. Default is 3.
        nr_partitions (int): Number of partitions in m/z dimension. Default is 100.
        warp_enabled (bool): Enable non-linear retention time transformation. Default is True.
        warp_rt_tol (float): RT tolerance for the LOWESS fit. Default is 5.0.
        warp_mz_tol (float): m/z tolerance for the LOWESS fit. Default is 0.05.
        warp_max_pairwise_log_fc (float): Maximum absolute log10 fold change threshold for pairing. Default is 0.5.
        warp_min_rel_cc_size (float): Minimum relative connected component size. Default is 0.5.
        warp_max_nr_conflicts (int): Allow up to this many conflicts per connected component for alignment. Default is 0.
        link_rt_tol (float): Width of RT tolerance window for linking (seconds). Default is 30.0.
        link_mz_tol (float): m/z tolerance for linking features (ppm or Da). Default is 10.0.
        link_charge_merging (str): Charge merging strategy for linking. Default is "With_charge_zero".
        link_adduct_merging (str): Adduct merging strategy for linking. Default is "Any".
        distance_RT_exponent (float): Exponent for normalized RT differences. Default is 1.0.
        distance_RT_weight (float): Weight factor for final RT distances. Default is 1.0.
        distance_MZ_exponent (float): Exponent for normalized m/z differences. Default is 2.0.
        distance_MZ_weight (float): Weight factor for final m/z distances. Default is 1.0.
        distance_intensity_exponent (float): Exponent for differences in relative intensity. Default is 1.0.
        distance_intensity_weight (float): Weight factor for final intensity distances. Default is 1.0.
        distance_intensity_log_transform (str): Log-transform intensities. Default is "enabled".
        LOWESS_span (float): Fraction of datapoints for each local regression. Default is 0.666666666666667.
        LOWESS_num_iterations (int): Number of robustifying iterations for LOWESS fitting. Default is 3.
        LOWESS_delta (float): Parameter for LOWESS computations (negative auto-computes). Default is -1.0.
        LOWESS_interpolation_type (str): Method for interpolation between datapoints. Default is "cspline".
        LOWESS_extrapolation_type (str): Method for extrapolation outside data range. Default is "four-point-linear".
    """

    rt_tol: float = 5.0
    mz_max_diff: float = 0.01
    rt_pair_distance_frac: float = 0.5
    mz_pair_max_distance: float = 0.01
    num_used_points: int = 1000
    save_features: bool = False
    skip_blanks: bool = False
    algorithm: str = "kd"

    # KD algorithm specific parameters
    min_samples: int = 3
    nr_partitions: int = 100
    warp_enabled: bool = True
    warp_rt_tol: float = 5.0
    warp_mz_tol: float = 0.05
    warp_max_pairwise_log_fc: float = 0.5
    warp_min_rel_cc_size: float = 0.5
    warp_max_nr_conflicts: int = 0
    link_rt_tol: float = 30.0
    link_mz_tol: float = 10.0
    link_charge_merging: str = "With_charge_zero"
    link_adduct_merging: str = "Any"
    distance_RT_exponent: float = 1.0
    distance_RT_weight: float = 1.0
    distance_MZ_exponent: float = 2.0
    distance_MZ_weight: float = 1.0
    distance_intensity_exponent: float = 1.0
    distance_intensity_weight: float = 1.0
    distance_intensity_log_transform: str = "enabled"
    LOWESS_span: float = 0.666666666666667
    LOWESS_num_iterations: int = 3
    LOWESS_delta: float = -1.0
    LOWESS_interpolation_type: str = "cspline"
    LOWESS_extrapolation_type: str = "four-point-linear"

    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "rt_tol": {
                "dtype": float,
                "description": "Maximum retention time difference for alignment (seconds)",
                "default": 5.0,
                "min_value": 1.0,
                "max_value": 30.0,
            },
            "mz_max_diff": {
                "dtype": float,
                "description": "Maximum m/z difference for alignment (Da)",
                "default": 0.01,
                "min_value": 0.001,
                "max_value": 0.05,
            },
            "rt_pair_distance_frac": {
                "dtype": float,
                "description": "Fraction of RT difference for pair distance calculation",
                "default": 0.2,
                "min_value": 0.1,
                "max_value": 1.0,
            },
            "mz_pair_max_distance": {
                "dtype": float,
                "description": "Maximum m/z pair distance (Da)",
                "default": 0.01,
                "min_value": 0.001,
                "max_value": 0.2,
            },
            "num_used_points": {
                "dtype": int,
                "description": "Number of points used for alignment",
                "default": 1000,
                "min_value": 10,
                "max_value": 10000,
            },
            "save_features": {
                "dtype": bool,
                "description": "Whether to save features after alignment",
                "default": False,
            },
            "skip_blanks": {
                "dtype": bool,
                "description": "Whether to skip blank samples during alignment",
                "default": False,
            },
            "algorithm": {
                "dtype": str,
                "description": "Alignment algorithm to use",
                "default": "pc",
                "allowed_values": ["pc", "kd"],
            },
            # KD algorithm specific parameters
            "min_samples": {
                "dtype": int,
                "description": "Minimum number of samples required for KD alignment algorithm",
                "default": 3,
                "min_value": 2,
                "max_value": 1000,
            },
            "nr_partitions": {
                "dtype": int,
                "description": "Number of partitions in m/z dimension for KD algorithm",
                "default": 100,
                "min_value": 1,
                "max_value": 1000,
            },
            "warp_enabled": {
                "dtype": bool,
                "description": "Enable non-linear retention time transformation for KD algorithm",
                "default": True,
            },
            "warp_rt_tol": {
                "dtype": float,
                "description": "RT tolerance for the LOWESS fit in KD algorithm (seconds)",
                "default": 5.0,
                "min_value": 0.1,
                "max_value": 60.0,
            },
            "warp_mz_tol": {
                "dtype": float,
                "description": "m/z tolerance for the LOWESS fit in KD algorithm (Da)",
                "default": 0.05,
                "min_value": 0.001,
                "max_value": 1.0,
            },
            "warp_max_pairwise_log_fc": {
                "dtype": float,
                "description": "Maximum absolute log10 fold change between two compatible signals during compatibility graph construction in KD algorithm",
                "default": 0.5,
                "min_value": -1.0,
                "max_value": 10.0,
            },
            "warp_min_rel_cc_size": {
                "dtype": float,
                "description": "Minimum relative connected component size for KD algorithm",
                "default": 0.5,
                "min_value": 0.0,
                "max_value": 1.0,
            },
            "warp_max_nr_conflicts": {
                "dtype": int,
                "description": "Allow up to this many conflicts (features from the same map) per connected component to be used for alignment (-1 means allow any number of conflicts)",
                "default": 0,
                "min_value": -1,
                "max_value": 1000,
            },
            "link_rt_tol": {
                "dtype": float,
                "description": "Width of RT tolerance window for linking in KD algorithm (seconds)",
                "default": 30.0,
                "min_value": 0.0,
                "max_value": 300.0,
            },
            "link_mz_tol": {
                "dtype": float,
                "description": "m/z tolerance for linking features in KD algorithm (ppm or Da)",
                "default": 10.0,
                "min_value": 0.0,
                "max_value": 100.0,
            },
            "link_charge_merging": {
                "dtype": str,
                "description": "Charge merging strategy for linking features in KD algorithm",
                "default": "With_charge_zero",
                "allowed_values": ["Identical", "With_charge_zero", "Any"],
            },
            "link_adduct_merging": {
                "dtype": str,
                "description": "Adduct merging strategy for linking features in KD algorithm",
                "default": "Any",
                "allowed_values": ["Identical", "With_unknown_adducts", "Any"],
            },
            "distance_RT_exponent": {
                "dtype": float,
                "description": "Normalized RT differences are raised to this power in KD algorithm",
                "default": 1.0,
                "min_value": 0.0,
                "max_value": 10.0,
            },
            "distance_RT_weight": {
                "dtype": float,
                "description": "Final RT distances are weighted by this factor in KD algorithm",
                "default": 1.0,
                "min_value": 0.0,
                "max_value": 100.0,
            },
            "distance_MZ_exponent": {
                "dtype": float,
                "description": "Normalized m/z differences are raised to this power in KD algorithm",
                "default": 2.0,
                "min_value": 0.0,
                "max_value": 10.0,
            },
            "distance_MZ_weight": {
                "dtype": float,
                "description": "Final m/z distances are weighted by this factor in KD algorithm",
                "default": 1.0,
                "min_value": 0.0,
                "max_value": 100.0,
            },
            "distance_intensity_exponent": {
                "dtype": float,
                "description": "Differences in relative intensity are raised to this power in KD algorithm",
                "default": 1.0,
                "min_value": 0.0,
                "max_value": 10.0,
            },
            "distance_intensity_weight": {
                "dtype": float,
                "description": "Final intensity distances are weighted by this factor in KD algorithm",
                "default": 1.0,
                "min_value": 0.0,
                "max_value": 100.0,
            },
            "distance_intensity_log_transform": {
                "dtype": str,
                "description": "Log-transform intensities in KD algorithm distance calculation",
                "default": "enabled",
                "allowed_values": ["enabled", "disabled"],
            },
            "LOWESS_span": {
                "dtype": float,
                "description": "Fraction of datapoints to use for each local regression in LOWESS fitting",
                "default": 0.666666666666667,
                "min_value": 0.0,
                "max_value": 1.0,
            },
            "LOWESS_num_iterations": {
                "dtype": int,
                "description": "Number of robustifying iterations for LOWESS fitting",
                "default": 3,
                "min_value": 0,
                "max_value": 10,
            },
            "LOWESS_delta": {
                "dtype": float,
                "description": "Nonnegative parameter for LOWESS computations (negative value auto-computes)",
                "default": -1.0,
                "min_value": -1.0,
                "max_value": 1000.0,
            },
            "LOWESS_interpolation_type": {
                "dtype": str,
                "description": "Method to use for interpolation between datapoints computed by LOWESS",
                "default": "cspline",
                "allowed_values": ["linear", "cspline", "akima"],
            },
            "LOWESS_extrapolation_type": {
                "dtype": str,
                "description": "Method to use for extrapolation outside the data range in LOWESS",
                "default": "four-point-linear",
                "allowed_values": [
                    "two-point-linear",
                    "four-point-linear",
                    "global-linear",
                ],
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

        # Range validation for numeric types
        if expected_dtype in (int, float) and isinstance(value, (int, float)):
            if "min_value" in metadata and value < metadata["min_value"]:
                return False
            if "max_value" in metadata and value > metadata["max_value"]:
                return False

        # Allowed values validation for string types
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
