"""
Module for handling communication and routing with the Houdini Digital Asset (HDA) for the Conductor plugin.

This module manages interactions between the HDA and various components of the Conductor plugin,
including connection handling, parameter callbacks, menu population, and payload updates.
It serves as the central routing mechanism for user interactions with the Conductor UI.
"""

import hou
import os
import re

from ciohoudini import (
    driver,
    instances,
    project,
    software,
    frames,
    environment,
    errors,
    context,
    assets,
    payload,
    submit,
    miscellaneous,
    render_rops,
    rops,
    usd_operations
)

from ciocore import data as coredata

import ciocore.config
import ciocore.api_client
import ciohoudini.const as k


try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

# Configure logging with a specific log file
ciocore.loggeria.setup_conductor_logging(log_filename="houdini_submitter.log")
# Register the API client for Conductor
ciocore.api_client.ApiClient.register_client(client_name="ciohoudini", client_version=k.VERSION)

# Define fixtures directory for Conductor
fixtures_dir = os.path.expanduser(os.path.join("~", "conductor_fixtures"))
# Initialize coredata for Houdini
coredata.init("houdini")
coredata.set_fixtures_dir("")

# Set default task context (first:1, last:1, step:1)
context.set_for_task()

# Regular expression for matching multi-parameter names (e.g., parm_1, parm_2)
MULTI_PARM_RE = re.compile(r"^([a-zA-Z0-9_]+_)\d+$")

# List of parameters that trigger payload updates when changed
AFFECTS_PAYLOAD = (
    "connect",
    "title",
    "project",
    "instance_type_family",
    "instance_type",
    "preemptible",
    "retries",
    "host_version",
    "driver_version",
    "chunk_size",
    "frame_range",
    "use_custom_frames",
    "use_scout_frames",
    "scout_frames",
    "rop_checkbox_",
    "rop_path_",
    "rop_frame_range_",
    "rop_use_scout_frames_",
    "add_hdas",
    "display_tasks",
    "do_asset_scan",
    "environment_kv_pairs",
    "env_key_",
    "env_value_",
    "env_excl_",
    "do_email",
    "email_addresses",
    "clear_all_assets",
    "browse_files",
    "browse_folder",
    "location_tag",
    "use_daemon",
    "add_variable",
    "add_existing_variable",
    "add_plugin",
    "extra_plugins",
    "extra_plugin_",
    "copy_script",
    "reload_render_rops",
    "update_render_rops",
    "apply_to_all_render_rops",
    "select_all_render_rops",
    "deselect_all_render_rops",
    "usd_filepath",
    "browse_usd_files",
    "driver_path",
    "override_image_output",
    "use_usd_scrapping_only",
    "driver_version",
    "render_delegate"
)

# Dictionary mapping menu parameters to their population functions
MENUS = {
    "instance_type": instances.populate_menu,
    "project": project.populate_menu,
    "host_version": software.populate_host_menu,
    "driver_version": software.populate_driver_menu,
    "frame_range_source": frames.populate_frame_range_menu,
    "extra_plugin_": software.populate_extra_plugin_menu,
}

# Parameters to lock when a node is created
LOCK_ON_CREATE = ["asset_regex", "asset_excludes"]

# Parameters with expressions requiring event callbacks for payload updates
NEEDS_PAYLOAD_CALLBACK = [
    "output_folder",
    "render_script",
    "frame_range",
    "title",
    "rop_checkbox_",
    "rop_path_",
    "rop_frame_range_",
    "rop_use_scout_frames_",
    "driver_path",
    "override_image_output",
]


def connect(node, **kwargs):
    """
    Establish a connection to Conductor data.

    Retrieves projects, hardware, and software information, and updates node parameters
    to reflect the connection status.

    Args:
        node: Conductor Submitter node to connect.
        **kwargs: Additional arguments, including:
            - force (bool): Whether to force a data refresh (default: True).
    """
    force = kwargs.get("force", True)
    try:
        # Attempt to fetch Conductor data
        try:
            logger.debug("Fetching Conductor data")
            coredata.data(force=force)
        except Exception as e:
            logger.error("Error fetching Conductor data: {}".format(e))
            display_connection_failed_message(node)
            return
        # Ensure valid selections for project, instance, and software
        project.ensure_valid_selection(node)
        instances.ensure_valid_selection(node)
        software.ensure_valid_selection(node)
    except Exception as e:
        logger.error("Error connecting to Conductor: {}".format(e))

    # Update connection status
    if coredata.valid():
        rops.set_parameter_value(node, "is_connected", 1)
        # Check hardware provider for preemptible option visibility
        hardware = coredata.data().get("instance_types")
        if hardware.provider in ["cw"]:
            rops.set_parameter_value(node, "cw_connection", 1)
        else:
            rops.set_parameter_value(node, "cw_connection", 0)
    else:
        display_connection_failed_message(node)


def display_connection_failed_message(node):
    """
    Display an error message when the connection to Conductor fails.

    Args:
        node: Conductor Submitter node associated with the connection attempt.
    """
    hou.ui.displayMessage(
        "Connection to Conductor failed. Please check your network connection and verify your credentials and try again.",
        severity=hou.severityType.Error
    )


def on_created(node, **kwargs):
    """
    Initialize the state of a newly created Houdini node for the Conductor plugin.

    Locks specific parameters to prevent user modification, sets default values for
    key parameters (e.g., scout frames, preemptible, frame range source), populates
    the frame range menu, updates render ROP frame ranges, and completes initialization
    by calling on_loaded.

    Args:
        node: The newly created Houdini node to initialize.
        **kwargs: Additional arguments passed to on_loaded for further initialization.
    """
    # Lock specified parameters
    for parm in LOCK_ON_CREATE:
        node.parm(parm).lock(True)

    # Set default values for parameters
    node.parm("scout_frames").set("fml:3")
    preemptible_parm = node.parm("preemptible")
    if preemptible_parm:
        preemptible_parm.set(True)

    frame_range_source_parm = node.parm("frame_range_source")
    if frame_range_source_parm:
        frame_range_source_parm.set("Houdini playbar")

    # Populate frame range menu and update render ROP frame range
    frames.populate_frame_range_menu(node)
    frames.update_render_rop_frame_range(node)

    node.setUserData('scheduler_node_path', node.path())

    # Complete initialization with on_loaded
    on_loaded(node, **kwargs)


def on_loaded(node, **kwargs):
    """
    Initialize node state when it is loaded.

    Adds callbacks for parameters with expressions, ensures valid selections, and updates
    the payload preview panel.

    Args:
        node: Conductor Submitter node being loaded.
        **kwargs: Additional arguments, including:
            - force (bool): Whether to force data refresh (default: False).
    """
    kwargs["force"] = False
    # Add callbacks for parameters with expressions
    node.addParmCallback(payload.set_preview_panel, NEEDS_PAYLOAD_CALLBACK)
    # Ensure valid selections for project, instance, and software
    project.ensure_valid_selection(node)
    instances.ensure_valid_selection(node)
    software.ensure_valid_selection(node)

    # Update payload preview for non-generator nodes
    node_type = rops.get_node_type(node)
    if node_type not in ["generator"]:
        payload.set_preview_panel(node, **kwargs)

    # Set log file path label
    node.parm('log_label').set(ciocore.loggeria.LOG_PATH)


def update_connection(node, **kwargs):
    """
    Verify and update the connection status of the node.

    Args:
        node: Conductor Submitter node to check.
        **kwargs: Additional arguments (unused).
    """
    is_connected = rops.get_parameter_value(node, "is_connected")
    if is_connected == 0 and coredata.valid():
        rops.set_parameter_value(node, "is_connected", 1)


def populate_menu(node, parm, **kwargs):
    """
    Dynamically populate a menu based on the parameter.

    Uses the MENUS dictionary to map parameters to their population functions.
    Handles both single and multi-parameters.

    Args:
        node: Conductor Submitter node containing the menu.
        parm: Parameter object for the menu.
        **kwargs: Additional arguments passed to the population function.

    Returns:
        The result of the menu population function.
    """
    update_connection(node, **kwargs)
    with errors.show():
        menu_key = parm.name()
        # Handle multi-parameters by extracting the base name
        match = MULTI_PARM_RE.match(menu_key)
        if match:
            menu_key = match.group(1)
        # Call the appropriate menu population function
        return MENUS.get(menu_key, noop)(node)



def on_updated(node, **kwargs):
    """
    Handle changes based on input connection make/break.

    Currently a placeholder for driver-related updates (e.g., Arnold, Mantra).

    Args:
        node: Conductor Submitter node with input changes.
        **kwargs: Additional arguments (unused).
    """
    pass


def on_input_changed(node, **kwargs):
    """
    Handle changes based on input connection make/break.

    Updates driver input and ensures valid software selections, refreshing the payload preview.

    Args:
        node: Conductor Submitter node with input changes.
        **kwargs: Additional arguments passed to payload update.
    """
    with errors.show():
        driver.update_input_node(node)
        software.ensure_valid_selection(node)
        # Update payload preview for non-generator nodes
        node_type = rops.get_node_type(node)
        if node_type not in ["generator"]:
            payload.set_preview_panel(node, **kwargs)


# Dictionary mapping parameters to their handler functions
PARM_HANDLERS = {
    "connect": connect,
    "instance_type_family": instances.ensure_valid_selection,
    "use_custom_frames": frames.on_use_custom,
    "clear_all_assets": assets.clear_all_assets,
    "browse_files": assets.browse_files,
    "browse_folder": assets.browse_folder,
    "add_hdas": assets.add_hdas,
    "submit": submit.invoke_submission_dialog,
    "export_script": submit.export_script,
    "add_variable": environment.add_variable,
    "add_existing_variable": environment.add_existing_variables,
    "add_plugin": software.add_plugin,
    "frame_range_source": frames.update_frame_range,
    "reload_render_rops": render_rops.reload_render_rops,
    "update_render_rops": render_rops.update_render_rops,
    "apply_to_all_render_rops": render_rops.apply_script_to_all_render_rops,
    "select_all_render_rops": render_rops.select_all_render_rops,
    "deselect_all_render_rops": render_rops.deselect_all_render_rops,
    "copy_script": miscellaneous.copy_render_script,
    "log_level": miscellaneous.change_log_level,
    "output_folder": rops.query_output_folder,
    "render_delegate": rops.set_render_software,
    "usd_filepath": rops.set_usd_path,
    "task_template_source": rops.set_default_task_template,
    "browse_usd_files": usd_operations.browse_usd_file,
    "generate": rops.generate_solaris_nodes,
    "driver_version": software.ensure_valid_selection,
    "host_version": software.ensure_valid_selection,
}


def noop(node, **kwargs):
    """
    Placeholder function for parameters with no specific handler.

    Args:
        node: Conductor Submitter node (unused).
        **kwargs: Additional arguments (unused).
    """
    pass


def on_change(node, **kwargs):
    """
    Route parameter change events to their respective handlers.

    Executes handlers from PARM_HANDLERS and updates the payload preview if needed.

    Args:
        node: Conductor Submitter node with changed parameter.
        **kwargs: Additional arguments, including:
            - parm_name (str): Name of the changed parameter.
    """
    parm_name = kwargs["parm_name"]
    with errors.show():
        # Get and execute handler(s) for the parameter
        funcs = PARM_HANDLERS.get(parm_name, noop)
        if not isinstance(funcs, list):
            funcs = [funcs]
        for func in funcs:
            func(node, **kwargs)

        # Update payload preview for parameters affecting the payload
        if parm_name.startswith(AFFECTS_PAYLOAD):
            node_type = rops.get_node_type(node)
            if node_type not in ["generator"]:
                payload.set_preview_panel(node, **kwargs)


def on_action_button(node, **kwargs):
    """
    Handle action button clicks for specific parameters.

    Processes actions for removing assets, environment variables, or plugins,
    and updates the payload preview.

    Args:
        node: Conductor Submitter node with the action button.
        **kwargs: Additional arguments, including:
            - parmtuple: Parameter tuple of the button.
            - script_multiparm_index: Index for multi-parameter actions.
    """
    with errors.show():
        node_type = rops.get_node_type(node)
        parmtuple = kwargs["parmtuple"]

        # Handle asset removal
        if parmtuple.name().startswith("extra_asset_"):
            index = kwargs["script_multiparm_index"]
            assets.remove_asset(node, index)
            if node_type not in ["generator"]:
                payload.set_preview_panel(node, **kwargs)
            return

        # Handle environment variable removal
        if parmtuple.name().startswith("env_excl_"):
            index = kwargs["script_multiparm_index"]
            environment.remove_variable(node, index)
            if node_type not in ["generator"]:
                payload.set_preview_panel(node, **kwargs)
            return

        # Handle plugin removal
        if parmtuple.name().startswith("extra_plugin_"):
            index = kwargs["script_multiparm_index"]
            software.remove_plugin(node, index)
            if node_type not in ["generator"]:
                payload.set_preview_panel(node, **kwargs)
            return