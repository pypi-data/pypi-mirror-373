"""
io_manager.py
-------------

This module provides functions for logging and saving per-generation data
during the evolutionary optimization workflow.
"""

import os
import json
import time
import csv
import numpy as np
import logging
from typing import Optional

import yaml

def make_serializable(obj):
    """
    Recursively converts non-serializable objects to types that can be JSON-serialized.
    """
    # Convert NumPy arrays to lists.
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    # Convert NumPy scalars to native Python types.
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    # Recursively process dictionaries.
    elif isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            # Ensure keys are of valid JSON types (str, int, float, bool, or None).
            if not isinstance(key, (str, int, float, bool)) and key is not None:
                key = str(key)
            new_dict[key] = make_serializable(value)
        return new_dict
    # Process lists and tuples.
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(item) for item in obj]
    # If the object is already a basic type, return it as is.
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    # Fallback for other types: use string representation.
    else:
        return str(obj)

def save_generation_data(generation, data, output_directory, filename_prefix="generation_data"):
    """
    Saves per-generation data to a JSON file.

    Parameters
    ----------
    generation : int
        Current generation index.
    data : dict
        Dictionary containing information about this generation (objectives, features,
        energies, selected indices, etc.). Must be JSON-serializable.
    output_directory : str
        Path where the file will be saved.
    filename_prefix : str, optional
        Prefix for the output file name. By default 'generation_data'.

    Returns
    -------
    str
        Full path to the file that was saved.
    """
    os.makedirs(output_directory, exist_ok=True)

    # Construct a filename that includes the generation number
    filename = f"{filename_prefix}_gen{generation}.json"
    filepath = os.path.join(output_directory, filename)

    data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

    serializable_data = make_serializable(data)

    # Write data to JSON
    with open(filepath, 'w') as f:
        json.dump(serializable_data, f, indent=4, sort_keys=True)

    return filepath
