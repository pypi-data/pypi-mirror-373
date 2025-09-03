"""
Study Parameters Module for study operations.

This module contains parameter management functions for the Study class,
similar to the sample parameters module but for study-level operations.
"""

from __future__ import annotations


def store_history(self, keys, value):
    """
    Store parameters in a nested dictionary structure.

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
    Retrieve parameters from nested dictionary structure.

    Parameters:
        keys (list): List of keys to identify the position in nested dicts

    Returns:
        The value at the specified location, or None if not found
    """
    if not isinstance(keys, list) or len(keys) == 0:
        raise ValueError("keys must be a non-empty list")

    current_dict = self.parameters
    for key in keys:
        if isinstance(current_dict, dict) and key in current_dict:
            current_dict = current_dict[key]
        else:
            return None

    return current_dict


def update_parameters(self, **kwargs):
    """
    Update study parameters using the new parameter system.

    Parameters:
        **kwargs: Keyword arguments for parameter updates. Can include:
                 - Study parameter defaults instances to set parameters
                 - Individual parameter names and values
    """
    # Handle parameter overrides from kwargs
    for key, value in kwargs.items():
        # Check if it's a parameter defaults instance
        if hasattr(value, "to_dict") and callable(getattr(value, "to_dict")):
            # Store the parameter object
            self.store_history([key], value.to_dict())
        else:
            # Store individual parameter
            self.store_history([key], value)


def get_parameters_property(self):
    """
    Property getter to provide backward compatibility for parameter access.
    Returns a dictionary that combines nested parameter objects.
    """
    # Create a combined view
    result = dict(self.parameters) if hasattr(self, "parameters") else {}

    return result


def set_parameters_property(self, value):
    """Property setter to allow setting parameters for backward compatibility."""
    if isinstance(value, dict):
        self.parameters = value
    else:
        raise ValueError("parameters must be a dictionary")
