"""
Module for managing render ROPs in the Conductor plugin for Houdini.

This module handles the addition, removal, and updating of render ROPs in the UI,
retrieves ROP data, and resolves output paths for the submission payload.
Supports driver ROPs (out network) and usdrender_rop nodes (stage network).
"""

import hou
import os

from ciohoudini import (
    driver,
    frames,
    rops,
)
from ciohoudini.util import rop_error_handler

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")


@rop_error_handler(error_message="Error adding render ROP to UI")
def add_one_render_rop(rop, node, next_index, network, render_rops_dict=None):
    """
    Add a single render ROP to the UI.

    Configures UI parameters for the ROP, including checkbox, path, and frame range.

    Args:
        rop: Houdini ROP node to add.
        node: Conductor Submitter node containing the render ROP parameters.
        next_index: Index for the new ROP entry in the UI.
        network: Network type ('out' or 'stage').
        render_rops_dict: Optional dictionary with stored ROP data for restoration.
    """
    if not rop:
        return None
    # Default to checked state
    rop_checkbox = True
    # Construct ROP path
    rop_path = rop.path() or f"/{network}/{rop.name()}"
    # Determine frame range based on ROP type
    if rop.type().name() == 'usdrender_rop':
        rop_frame_range = frames.get_all_rop_frame_range(node, rop_path)
    else:
        rop_frame_range = frames.get_all_rop_frame_range(node, rop_path)

    # Restore stored data if available
    if rop_path and render_rops_dict:
        key = rop_path.replace("/", "")
        if key in render_rops_dict:
            rop_frame_range = render_rops_dict[key].get('frame_range', '1-1')
            rop_checkbox = render_rops_dict[key].get('rop_checkbox', True)

    # Update UI parameters
    render_rops_parm = node.parm("render_rops")
    if render_rops_parm:
        render_rops_parm.set(next_index)

    rop_checkbox_parm = node.parm(f"rop_checkbox_{next_index}")
    if rop_checkbox_parm:
        rop_checkbox_parm.set(rop_checkbox)

    rop_path_parm = node.parm(f"rop_path_{next_index}")
    if rop_path_parm:
        rop_path_parm.set(rop_path)

    rop_frame_range_parm = node.parm(f"rop_frame_range_{next_index}")
    if rop_frame_range_parm:
        rop_frame_range_parm.set(rop_frame_range)


@rop_error_handler(error_message="Error retrieving render ROP data")
def get_render_rop_data(node):
    """
    Retrieve render ROP data from the UI.

    Collects data for checked ROPs, including path and frame range.

    Args:
        node: Conductor Submitter node containing render ROP parameters.

    Returns:
        list: List of dictionaries with ROP path and frame range.
    """
    render_rops_data = []
    if node.parm("render_rops"):
        # Iterate over all ROP entries
        for i in range(1, node.parm("render_rops").eval() + 1):
            if node.parm(f"rop_checkbox_{i}").eval():
                render_rops_data.append({
                    "path": node.parm(f"rop_path_{i}").evalAsString(),
                    "frame_range": node.parm(f"rop_frame_range_{i}").evalAsString(),
                })
    return render_rops_data


@rop_error_handler(error_message="Error storing render ROP data")
def store_current_render_rop_data(node):
    """
    Store current render ROP data from the UI.

    Creates a dictionary mapping ROP paths to their checkbox state and frame range.

    Args:
        node: Conductor Submitter node containing render ROP parameters.

    Returns:
        dict: Dictionary of ROP data keyed by normalized path.
    """
    render_rops_dict = {}
    for i in range(1, node.parm("render_rops").eval() + 1):
        path = node.parm(f"rop_path_{i}").evalAsString()
        if path:
            key = path.replace("/", "")
            if key not in render_rops_dict:
                render_rops_dict[key] = {}
                render_rops_dict[key]["rop_checkbox"] = node.parm(f"rop_checkbox_{i}").eval()
                render_rops_dict[key]["frame_range"] = node.parm(f"rop_frame_range_{i}").evalAsString()
    return render_rops_dict


@rop_error_handler(error_message="Error adding render ROPs to UI")
def add_render_rops(node, render_rops_dict=None):
    """
    Add all render ROPs to the UI.

    Supports driver ROPs (out network) and usdrender_rop nodes (stage network).

    Args:
        node: Conductor Submitter node to add ROPs to.
        render_rops_dict: Optional dictionary with stored ROP data for restoration.
    """
    next_index = 1
    # Add driver ROP if it exists
    driver_rop = driver.get_driver_node(node)
    if driver_rop:
        add_one_render_rop(driver_rop, node, next_index, "out", render_rops_dict=render_rops_dict)
    # Add stage ROPs
    render_ropes = get_stage_render_rops()
    if render_ropes:
        for rop in render_ropes:
            render_ropes_param = node.parm("render_rops")
            if render_ropes_param:
                next_index = render_ropes_param.eval() + 1
            add_one_render_rop(rop, node, next_index, "stage", render_rops_dict=render_rops_dict)


@rop_error_handler(error_message="Error retrieving stage render ROPs")
def get_stage_render_rops():
    """
    Retrieve all non-bypassed usdrender_rop nodes in the stage network.

    Returns:
        list: List of usdrender_rop nodes.
    """
    stage_render_ropes = []
    stage_node_list = hou.node('/stage').allSubChildren()
    # Iterate over stage nodes to find usdrender_rop nodes
    for rop in stage_node_list:
        if rop and rop.type().name() == 'usdrender_rop' and not rop.isBypassed():
            stage_render_ropes.append(rop)
    return stage_render_ropes


@rop_error_handler(error_message="Error removing render ROP row")
def remove_rop_row(node):
    """
    Remove the last render ROP entry from the UI.

    Clears parameters for the last entry and decrements the ROP count.

    Args:
        node: Conductor Submitter node containing render ROP parameters.
    """
    curr_count = node.parm("render_rops").eval()
    node.parm(f"rop_checkbox_{curr_count}").set(False)
    node.parm(f"rop_path_{curr_count}").set("")
    node.parm(f"rop_frame_range_{curr_count}").set("")
    node.parm("render_rops").set(curr_count - 1)


@rop_error_handler(error_message="Error removing all render ROP rows")
def remove_all_rop_rows(node):
    """
    Remove all render ROP entries from the UI.

    Clears all parameters and resets the ROP count to zero Dashboard.

    Args:
        node: Conductor Submitter node containing render ROP parameters.
    """
    curr_count = node.parm("render_rops").eval()
    for i in range(1, curr_count + 1):
        node.parm(f"rop_checkbox_{i}").set(False)
        node.parm(f"rop_path_{i}").set("")
        node.parm(f"rop_frame_range_{i}").set("")
    node.parm("render_rops").set(0)


@rop_error_handler(error_message="Error selecting all render ROPs")
def select_all_render_rops(node, **kwargs):
    """
    Select (check) all render ROPs in the UI.

    Args:
        node: Conductor Submitter node containing render ROP parameters.
        **kwargs: Additional arguments (unused).
    """
    curr_count = node.parm("render_rops").eval()
    for i in range(1, curr_count + 1):
        node.parm(f"rop_checkbox_{i}").set(True)


@rop_error_handler(error_message="Error deselecting all render ROPs")
def deselect_all_render_rops(node, **kwargs):
    """
    Deselect (uncheck) all render ROPs in the UI.

    Args:
        node: Conductor Submitter node containing render ROP parameters.
        **kwargs: Additional arguments (unused).
    """
    curr_count = node.parm("render_rops").eval()
    for i in range(1, curr_count + 1):
        node.parm(f"rop_checkbox_{i}").set(False)


@rop_error_handler(error_message="Error reloading render ROPs")
def reload_render_rops(node, **kwargs):
    """
    Reload render ROP data into the UI.

    Clears existing ROPs and re-adds them without preserving previous settings.

    Args:
        node: Conductor Submitter node containing render ROP parameters.
        **kwargs: Additional arguments (unused).
    """
    # Clear existing ROPs
    remove_all_rop_rows(node)
    # Re-add all ROPs
    add_render_rops(node, render_rops_dict=None)


@rop_error_handler(error_message="Error updating render ROPs")
def update_render_rops(node, **kwargs):
    """
    Update render ROP data in the UI.

    Preserves existing settings (checkbox state, frame range) while refreshing ROPs.

    Args:
        node: Conductor Submitter node containing render ROP parameters.
        **kwargs: Additional arguments (unused).
    """
    # Store current ROP data
    render_rops_dict = store_current_render_rop_data(node)
    # Clear existing ROPs
    remove_all_rop_rows(node)
    # Re-add ROPs with stored data
    add_render_rops(node, render_rops_dict=render_rops_dict)


@rop_error_handler(error_message="Error applying script to render ROPs")
def apply_script_to_all_render_rops(node, **kwargs):
    """
    Apply an image output script to all render ROPs.

    Args:
        node: Conductor Submitter node containing the override script parameter.
        **kwargs: Additional arguments (unused).
    """
    script = node.parm("override_image_output").evalAsString()
    curr_count = node.parm("render_rops").eval()
    # Apply script to each ROP
    for i in range(1, curr_count + 1):
        rop_path = node.parm(f"rop_path_{i}").evalAsString()
        driver.apply_image_output_script(rop_path, script)


@rop_error_handler(error_message="Error resolving output path for submission payload")
def resolve_payload(node, rop_path=None):
    """
    Resolve the output path for the submission payload.

    Ensures the output directory exists, creating it if necessary.

    Args:
        node: Conductor Submitter node to query output path from.
        rop_path: Optional path to a specific render ROP.

    Returns:
        dict: Dictionary with the output path.
    """
    output_path = ""
    # Query output folder
    output_path = rops.query_output_folder(node, rop_path=rop_path)
    if output_path:
        output_path = os.path.expandvars(output_path)
    # Create output directory if it doesn't exist
    #if output_path and not os.path.exists(output_path):
    #    os.makedirs(output_path)
    return {"output_path": output_path}