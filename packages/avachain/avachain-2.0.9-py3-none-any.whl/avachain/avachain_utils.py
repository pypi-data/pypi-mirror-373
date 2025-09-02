"""
Avachain Utilities - Resource management utilities.

This module provides utility functions for resource management and path handling,
particularly useful for development and PyInstaller packaged distributions.
"""

import os
import sys


def resource_path(relative_path):
    """
    Get absolute path to resource, works for both development and PyInstaller environments.

    This function handles path resolution in both development environments and
    when the application is packaged with PyInstaller. PyInstaller creates a
    temporary folder and stores path in sys._MEIPASS during runtime.

    Args:
        relative_path (str): The relative path to the resource file

    Returns:
        str: The absolute path to the resource

    Example:
        >>> path = resource_path('config/settings.json')
        >>> # Returns: '/absolute/path/to/config/settings.json'
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # In development, use the directory containing this file
        base_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(base_path, relative_path)
