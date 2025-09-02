"""
Module for generating and managing the submission payload in the Conductor plugin for Houdini.

This module orchestrates the creation of payload data for job submissions, integrating various
components such as job title, project, instances, software, environment, driver, frames, tasks,
and assets. It also updates the UI stats and preview panels.
"""

import json
import hou
import time

from ciohoudini import (
    job_title,
    project,
    instances,
    software,
    environment,
    driver,
    frames,
    task,
    assets,
    miscellaneous,
    render_rops,
    rops,
    util,
)

from ciohoudini.util import rop_error_handler

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

@rop_error_handler(error_message="Error updating stats panel")
def set_stats_panel(node, **kwargs):
    """
    Update the stats panel in the UI with frame-related statistics.

    Currently delegates to the frames module for updates, with potential for future expansion
    to include other statistics like cost estimates.

    Args:
        node: Conductor Submitter node containing stats parameters.
        **kwargs: Additional arguments passed to frames.set_stats_panel.
    """
    frames.set_stats_panel(node, **kwargs)

@rop_error_handler(error_message="Error refreshing LOP network")
def refresh_lop_network():
    """
    Force a refresh of the LOP network to ensure up-to-date data.

    Cooks the /stage LOP network node.
    """
    lop_network = hou.node("/stage")
    lop_network.cook(force=True)

@rop_error_handler(error_message="Error updating payload preview panel")
def set_preview_panel(node, **kwargs):
    """
    Update the payload preview panel in the UI.

    Generates and displays the JSON payload for submission, with options to limit tasks
    or include asset scans based on user input.

    Args:
        node: Conductor Submitter node containing the payload preview parameter.
        **kwargs: Additional arguments, including:
            - parm_name: Parameter name to check for asset scan trigger.
    """
    kwargs["task_limit"] = node.parm("display_tasks").eval()
    kwargs["do_asset_scan"] = (kwargs.get("parm_name") == "do_asset_scan")
    start_time = time.time()
    payload = resolve_payloads(node, **kwargs)
    end_time = time.time()
    duration = end_time - start_time
    logger.debug(f"resolve_payload (including network cook if any) took {duration:.4f} seconds.")
    if payload and len(payload) > 0:
        logger.debug(f"Creating payload ...")
        node.parm("payload").set(json.dumps(payload, indent=2))
        logger.debug(f"Payload created: {payload}")
    else:
        node.parm("payload").set("Unable to generate payload.")

@rop_error_handler(error_message="Error resolving payloads")
def resolve_payloads(node, **kwargs):
    """
    Generate the complete payload for job submission.

    Handles both single and multi-ROP nodes, including generator nodes, by collecting
    payloads for each render ROP or node configuration.

    Args:
        node: Conductor Submitter node to generate payload for.
        **kwargs: Additional arguments, including:
            - do_asset_scan: Boolean to trigger asset scanning.
            - rop_path: Path to a specific render ROP.
            - frame_range: Frame range for the payload.

    Returns:
        list: List of payload dictionaries, or empty list if node is invalid.
    """
    payload_list = []
    if not node:
        logger.debug("Unable to generate payload. Node is invalid")
        return payload_list
    node_type = rops.get_node_type(node)
    node_list = rops.get_node_list("multi_rop")
    if node_type in node_list:
        render_rop_data = render_rops.get_render_rop_data(node)
        if not render_rop_data:
            return None
        refresh_lop_network()
        for render_rop in render_rop_data:
            frame_range = render_rop.get("frame_range", None)
            kwargs["frame_range"] = frame_range
            rop_path = render_rop.get("path", None)
            kwargs["rop_path"] = rop_path
            payload = get_payload(node, **kwargs)
            if payload:
                payload_list.append(payload)
    else:
        if node_type not in ["generator"]:
            rop_path = None
            if node_type not in ["husk"]:
                rop_path = node.parm("driver_path").evalAsString()
            kwargs["rop_path"] = rop_path
            payload = get_payload(node, **kwargs)
            if payload:
                payload_list.append(payload)
        else:
            payload_list = get_generator_payload(node, **kwargs)
    return payload_list

@rop_error_handler(error_message="Error generating payload for generator node")
def get_generator_payload(node, **kwargs):
    """
    Generate payloads for render ROPs attached to a generator node.

    Retrieves ROP data and generates payloads by accessing corresponding conductor nodes
    within a connected subnet.

    Args:
        node: Conductor Submitter node (generator type) containing render ROPs.
        **kwargs: Additional arguments, including:
            - frame_range: Frame range for the payload.
            - rop_path: Path to a specific render ROP.
            - do_asset_scan: Boolean to trigger asset scanning.

    Returns:
        list: List of payload dictionaries, or None if no valid data is found.
    """
    render_rops_data = render_rops.get_render_rop_data(node)
    if not render_rops_data:
        return None
    refresh_lop_network()
    connected_subnet = None
    for input_node in node.outputs():
        if input_node and input_node.type().name() == "subnet":
            connected_subnet = input_node
            break
    if not connected_subnet:
        return None
    payload_list = []
    for render_rop in render_rops_data:
        rop_path = render_rop.get("path", None)
        frame_range = render_rop.get("frame_range", None)
        if not rop_path:
            continue
        rop_name = rop_path.split("/")[-1]
        conductor_node_name = f"conductor_{rop_name}"
        conductor_node = connected_subnet.node(conductor_node_name)
        if conductor_node:
            kwargs["frame_range"] = frame_range
            kwargs["rop_path"] = rop_path
            payload = get_payload(conductor_node, **kwargs)
            if payload:
                payload_list.append(payload)
        else:
            logger.debug(f"Conductor node {conductor_node_name} not found in subnet {connected_subnet.name()}.")
    return payload_list

@rop_error_handler(error_message="Error generating single payload")
def get_payload(node, **kwargs):
    """
    Generate a single payload for a node and optional ROP path.

    Combines data from various modules to create a complete payload dictionary.

    Args:
        node: Conductor Submitter node to generate payload for.
        **kwargs: Additional arguments, including:
            - rop_path: Path to a specific render ROP.
            - frame_range: Frame range for the payload.
            - do_asset_scan: Boolean to trigger asset scanning.

    Returns:
        dict: Payload dictionary, or None if node is invalid.
    """
    payload = {}
    if not node:
        logger.debug("Unable to generate payload. Conductor Node is invalid")
        return None
    rop_path = kwargs.get("rop_path", None)
    frame_range_to_use = kwargs.get("frame_range")
    if not frame_range_to_use:
        frame_range_to_use = node.parm("frame_range").evalAsString()
    payload.update(job_title.resolve_payload(node, rop_path=rop_path))
    payload.update(project.resolve_payload(node))
    payload.update(instances.resolve_payload(node))
    payload.update(software.resolve_payload(node))
    payload.update(environment.resolve_payload(node))
    payload.update(render_rops.resolve_payload(node, rop_path))
    payload.update(miscellaneous.resolve_payload(node))
    payload.update(frames.resolve_payload(node, frame_range=frame_range_to_use))
    payload.update(task.resolve_payload(node, **kwargs))
    payload.update(assets.resolve_payload(node, **kwargs))
    return payload