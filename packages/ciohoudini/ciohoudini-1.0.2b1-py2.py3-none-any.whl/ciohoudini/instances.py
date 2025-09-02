"""
Module for managing instance type selection in the Conductor plugin for Houdini.

This module handles the population of the instance type menu, ensures valid selections,
and resolves instance-related parameters for the submission payload.
"""

from ciocore import data as coredata
from ciohoudini import rops, util
from ciohoudini.util import rop_error_handler

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

@rop_error_handler(error_message="Error retrieving instance types")
def _get_instance_types(node):
    """
    Retrieve instance types based on the selected instance type family (CPU or GPU).

    Args:
        node: Conductor Submitter node containing the instance type family parameter.

    Returns:
        list: List of instance type dictionaries filtered by family.
    """
    family = node.parm("instance_type_family").eval()
    instances = coredata.data()["instance_types"]
    if instances:
        instances = instances.instance_types.values()
        # Filter instances by family
        return [item for item in instances if _is_family(item, family)]
    return []

@rop_error_handler(error_message="Error checking instance family")
def _is_family(item, family):
    """
    Check if an instance type belongs to the specified family (CPU or GPU).

    Args:
        item: Instance type dictionary containing GPU information.
        family: Instance type family ('cpu' or 'gpu').

    Returns:
        bool: True if the instance matches the family, False otherwise.
    """
    return ((family == "gpu") and item.get("gpu")) or ((family == "cpu") and not item.get("gpu"))

@rop_error_handler(error_message="Error populating instance type menu")
def populate_menu(node):
    """
    Populate the instance type menu in the UI.

    Retrieves instance types from coredata and formats them for the menu as a flat list
    of [name, description, name, description, ...].

    Args:
        node: Conductor Submitter node containing the instance type parameter.

    Returns:
        list: Flattened list of menu items, or a default item if not connected.
    """
    if not coredata.valid():
        return ["not_connected", "-- Not Connected --"]
    ensure_valid_selection(node)
    # Format instance types for menu
    return [el for item in _get_instance_types(node) for el in (item["name"], item["description"])]

@rop_error_handler(error_message="Error ensuring valid instance selection")
def ensure_valid_selection(node, **kwargs):
    """
    Ensure the instance type parameter has a valid selection.

    Sets the first available instance type if the current selection is invalid or if no
    instance types are available.

    Args:
        node: Conductor Submitter node containing the instance type parameter.
        **kwargs: Additional arguments (unused).
    """
    if not coredata.valid():
        return
    selected = node.parm("instance_type").eval()
    names = [i["name"] for i in _get_instance_types(node)]
    if not names:
        node.parm("instance_type").set("no_instance_types")
        return
    # Keep valid selection or set to first available
    if selected in names:
        node.parm("instance_type").set(selected)
    else:
        node.parm("instance_type").set(names[0])

@rop_error_handler(error_message="Error resolving instance payload")
def resolve_payload(node):
    """
    Generate the instance-related portion of the submission payload.

    Includes instance type, preemptible status, and retry policy if applicable.

    Args:
        node: Conductor Submitter node containing instance parameters.

    Returns:
        dict: Dictionary with instance type, preemptible status, and optional retry policy.
    """
    preemptible = False
    preemptible_check = rops.get_parameter_value(node, "preemptible")
    cw_connection = rops.get_parameter_value(node, "cw_connection")
    # If preemptible is checked and the parameter cw_connection is set to 1, set preemptible to True
    if preemptible_check and cw_connection == 1:
        preemptible = True
    result = {
        "instance_type": node.parm("instance_type").eval(),
        "preemptible": preemptible
    }

    # Add retry policy for preemptible instances with retries
    retries = rops.get_parameter_value(node, "retries")
    if preemptible and retries > 0:
        result["autoretry_policy"] = {"preempted": {"max_retries": retries}}
    return result