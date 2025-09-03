"""
Sample Parameters Module for individual sample operations.

This module contains parameter management functions for the Sample class.
"""

from __future__ import annotations


def store_history(self, keys, value):
    """
    Store parameters in self.history.

    Parameters:
        keys (list): List of keys to identify the position in nested dicts
        value: The value to store (can be a parameter object, dict, or any other value)
    """
    if not isinstance(keys, list) or len(keys) == 0:
        raise ValueError("keys must be a non-empty list")

    # Initialize self.history if it doesn't exist
    if not hasattr(self, "history"):
        self.history = {}

    # Navigate to the target location, creating nested dicts as needed
    current_dict = self.history
    for key in keys[:-1]:
        if key not in current_dict:
            current_dict[key] = {}
        elif not isinstance(current_dict[key], dict):
            # If the existing value is not a dict, replace it with a dict
            current_dict[key] = {}
        current_dict = current_dict[key]

    # Store the value at the final key
    current_dict[keys[-1]] = value


def get_parameters(self, keys):
    """
    Retrieve parameters from the sample_defaults object or nested history structure.

    Parameters:
        keys (list): List of keys to identify the position

    Returns:
        The value at the specified location, or None if not found
    """
    if not isinstance(keys, list) or len(keys) == 0:
        raise ValueError("keys must be a non-empty list")

    # If asking for sample parameters, get from self.parameters (sample_defaults object)
    if keys[0] == "sample":
        if len(keys) == 1:
            # Return the whole sample_defaults object as dict
            return self.parameters.to_dict() if hasattr(self.parameters, "to_dict") else None
        else:
            # Get specific parameter from sample_defaults object
            param_name = keys[1]
            if hasattr(self.parameters, param_name):
                return getattr(self.parameters, param_name)
            return None

    # Otherwise, look in history for processing parameters
    if not hasattr(self, "history"):
        return None

    current_dict = self.history
    for key in keys:
        if isinstance(current_dict, dict) and key in current_dict:
            current_dict = current_dict[key]
        else:
            return None

    return current_dict


def update_parameters(self, **kwargs):
    """
    Update sample parameters using the new parameter system.

    Parameters:
        **kwargs: Keyword arguments for parameter updates. Can include:
                 - A sample_defaults instance to set all parameters at once
                 - Individual parameter names and values (see sample_defaults for details)
    """
    # Import here to avoid circular imports
    from masster.sample.defaults.sample_def import (
        sample_defaults as SampleDefaults,
    )

    # Get current sample parameter object (should already be a sample_defaults instance)
    current_params = self.parameters

    # Handle parameter overrides from kwargs
    for key, value in kwargs.items():
        if isinstance(value, SampleDefaults):
            self.parameters = value
            break
        else:
            if hasattr(current_params, key):
                current_params.set(key, value, validate=True)

    # No need to store in history - self.parameters is the source of truth for sample params


def get_parameters_property(self):
    """
    Property getter to provide backward compatibility for parameter access.
    Returns a dictionary that provides access to sample parameters and history.
    """
    # Create a result dict with sample parameters
    result = {}

    # Add sample parameters from the sample_defaults object
    if hasattr(self.parameters, "to_dict"):
        result["sample"] = self.parameters.to_dict()

    # Add history (processing parameters)
    if hasattr(self, "history"):
        result.update(self.history)

    return result


def set_parameters_property(self, value):
    """Property setter to allow setting parameters for backward compatibility."""
    if isinstance(value, dict):
        self.parameters = value
    else:
        raise ValueError("parameters must be a dictionary")
