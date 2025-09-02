"""
Module for common utility functions in Houdini.

This module provides helper functions for working with Houdini Digital Assets (HDAs),
specifically for identifying non-built-in HDA definitions.
"""

import hou
import os

def get_plugin_definitions():
    """
    Retrieve HDA definitions that are not built-in to Houdini.

    Iterates through all node type categories and their node types, checking for
    definitions with instances that have a library file path outside the Houdini
    installation directory ($HFS).

    Returns:
        list: A list of HDA definition objects for non-built-in plugins.
    """
    result = []
    for category in hou.nodeTypeCategories().values():
        for node_type in category.nodeTypes().values():
            if node_type.instances():
                definition = node_type.definition()
                if definition:
                    path = definition.libraryFilePath()
                    if path and not path.startswith(os.environ["HFS"]):
                        result.append(definition)
    return result