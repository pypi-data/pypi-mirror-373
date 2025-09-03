"""
Module for managing project selection in the Conductor plugin for Houdini.

This module handles the population of the project menu, ensures valid project selections,
and resolves project-related parameters for the submission payload.
"""

from ciocore import data as coredata


def populate_menu(node):
    """
    Populate the project selection menu in the UI.

    Retrieves project names from coredata and formats them as a flat list of
    [name, name, name, name, ...] for the menu.

    Args:
        node: Conductor Submitter node containing the project parameter.

    Returns:
        list: Flattened list of menu items, or a default item if not connected.
    """
    # Return default item if not connected to Conductor
    if not coredata.valid():
        return ["not_connected", "-- Not Connected --"]
    # Ensure a valid project is selected
    ensure_valid_selection(node)
    # Format project names for menu
    return [el for p in coredata.data()["projects"] for el in [p, p]]


def ensure_valid_selection(node,**kwargs):
    """
    Ensure the project parameter has a valid selection.

    Check if no project are available.
    Sets the first available project

    Args:
        node: Conductor Submitter node containing the project parameter.
    """
    if not coredata.valid():
        return

    # Get current selection and available projects
    selected = node.parm("project").eval()
    projects = coredata.data()["projects"]

    # Handle case with no projects
    if not projects:
        node.parm("project").set("no_projects")
        return
    # Keep valid selection or set to first available
    if selected in projects:
        node.parm("project").set(selected)
    else:
        # Set to first project if current selection is invalid
        node.parm("project").set(coredata.data()["projects"][0])


def resolve_payload(node):
    """
    Generate the project-related portion of the submission payload.

    Retrieves the selected project from the node's UI parameter.

    Args:
        node: Conductor Submitter node containing the project parameter.

    Returns:
        dict: Dictionary with the selected project name.
    """
    return {"project": node.parm('project').eval()}