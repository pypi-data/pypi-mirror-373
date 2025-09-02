"""
Module for accessing and managing information about connected driver inputs in the Conductor plugin.

This module is specific to the Conductor::job node, handling input driver nodes (e.g., Karma, Arnold, Redshift)
to retrieve output paths, simulation status, and other driver-specific data. It provides utilities for
managing render output paths and updating the UI based on input connections.

Attributes:
    DRIVER_TYPES (dict): Mapping of driver types to their properties, including directory functions,
                        parameter names, simulation status, and Conductor product names.
    render_delegate_dict (dict): Mapping of render delegate names to their corresponding driver types.
"""

import hou
import os
from ciopath.gpath_list import PathList
from ciohoudini import render_rops, rops
from ciohoudini.util import rop_error_handler

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

def get_single_dirname(parm):
    """
    Extract the directory name from a parameter's evaluated path.

    Args:
        parm: Houdini parameter containing a file path.

    Returns:
        str: The directory name of the path, or an error message if invalid.
    """
    path = parm.eval()
    path = os.path.dirname(path)
    if not path:
        return f"INVALID FILENAME IN {parm.path()}"
    return path

def get_ris_common_dirname(parm):
    """
    Extract the common directory name from multiple RenderMan display parameters.

    Args:
        parm: Houdini parameter representing the number of displays (ri_displays).

    Returns:
        str: The common directory name for all display paths, or the dirname for a single path.
    """
    node = parm.node()
    num = parm.eval()
    path_list = PathList()
    for i in range(num):
        path = node.parm(f"ri_display_{i}").eval()
        if path:
            path_list.add(path)
    common_dirname = path_list.common_path().fslash()
    if num == 1:
        common_dirname = os.path.dirname(common_dirname)
    return common_dirname

def no_op(parm):
    """
    Placeholder function for unknown driver types.

    Args:
        parm: Houdini parameter (unused).

    Returns:
        str: A default error message.
    """
    return "UNKNOWN INPUT"

# Mapping of render delegate names to driver types
render_delegate_dict = {
    "karma_cpu": "karma",
    "karma_xpu": "karma",
    "arnold": "arnold",
    "redshift": "Redshift_ROP",
    "renderman": "ris::3.0",
    "vray": "vray_renderer",
}

# Mapping of driver types to their properties
DRIVER_TYPES = {
    "ifd": {
        "dirname_func": get_single_dirname,
        "parm_name": "vm_picture",
        "is_simulation": False,
        "conductor_product": "built-in: Mantra",
    },
    "vray_renderer": {
        "dirname_func": get_single_dirname,
        "parm_name": "SettingsOutput_img_file_path",
        "is_simulation": False,
        "conductor_product": "v-ray-houdini",
    },
    "baketexture::3.0": {
        "dirname_func": get_single_dirname,
        "parm_name": "vm_uvoutputpicture1",
        "is_simulation": False,
        "conductor_product": "built-in: Bake texture",
    },
    "arnold": {
        "dirname_func": get_single_dirname,
        "parm_name": "ar_picture",
        "is_simulation": False,
        "conductor_product": "arnold-houdini",
    },
    "ris::3.0": {
        "dirname_func": get_single_dirname,
        "parm_name": "ri_displays",
        "is_simulation": False,
        "conductor_product": "renderman-houdini",
    },
    "Redshift_ROP": {
        "dirname_func": get_single_dirname,
        "parm_name": "RS_outputFileNamePrefix",
        "is_simulation": False,
        "conductor_product": "redshift-houdini",
    },
    "karma": {
        "dirname_func": get_single_dirname,
        "parm_name": "picture",
        "is_simulation": False,
        "conductor_product": "built-in: karma-houdini",
    },
    "usdrender": {
        "dirname_func": get_single_dirname,
        "parm_name": "outputimage",
        "is_simulation": False,
        "conductor_product": "built-in: karma-houdini",
    },
    "usdrender_rop": {
        "dirname_func": get_single_dirname,
        "parm_name": "outputimage",
        "is_simulation": False,
        "conductor_product": "built-in: karma-houdini",
    },
    "geometry": {
        "dirname_func": get_single_dirname,
        "parm_name": "sopoutput",
        "is_simulation": False,
        "conductor_product": "built-in: Geometry cache",
    },
    "output": {
        "dirname_func": get_single_dirname,
        "parm_name": "dopoutput",
        "is_simulation": True,
        "conductor_product": "built-in: Simulation",
    },
    "dop": {
        "dirname_func": get_single_dirname,
        "parm_name": "dopoutput",
        "is_simulation": True,
        "conductor_product": "built-in: Simulation",
    },
    "opengl": {
        "dirname_func": get_single_dirname,
        "parm_name": "picture",
        "is_simulation": False,
        "conductor_product": "built-in: OpenGL render",
    },
    "unknown": {
        "dirname_func": no_op,
        "parm_name": None,
        "is_simulation": False,
        "conductor_product": "unknown driver",
    },
}

@rop_error_handler(error_message="Error applying image output script")
def apply_image_output_script(rop_path, script):
    """
    Apply an output script to a render ROP's output parameter if it is empty.

    Args:
        rop_path: Path to the render ROP node.
        script: Script or path to set as the output parameter value.
    """
    rop_node = hou.node(rop_path)
    if rop_node:
        driver_type = rop_node.type().name()
        callback = DRIVER_TYPES.get(driver_type, DRIVER_TYPES["unknown"])
        parm = rop_node.parm(callback["parm_name"])
        if parm:
            if not parm.eval():
                parm.set(script)
            else:
                logger.debug(f"Skipping parm: {parm.name()} with script {script}, parm is not empty")
        else:
            raise hou.NodeError(f"Could not find parm: {callback['parm_name']}")
    else:
        raise hou.NodeError(f"Could not find rop: {rop_path}")

@rop_error_handler(error_message="Error retrieving ROP image output", warning_only=True)
def get_rop_image_output(rop_path):
    """
    Retrieve the image output path from a render ROP's output parameter.

    Args:
        rop_path: Path to the render ROP node.

    Returns:
        str: The unexpanded string of the output parameter.

    Raises:
        hou.NodeError: If the ROP node, parameter cannot be found, or an unexpected error occurs.
        ValueError: If rop_path is not provided.
    """

    if not rop_path:
        logger.debug("ROP path not provided to get_rop_image_output")
        return None
    rop_node = hou.node(rop_path)
    if not rop_node:
        raise hou.NodeError(f"Could not find ROP node at path: {rop_path}")
    driver_type = rop_node.type().name()
    callback = DRIVER_TYPES.get(driver_type, DRIVER_TYPES["unknown"])
    parm_name = callback.get("parm_name")
    if not parm_name:
        raise hou.NodeError(f"No output parameter name defined for driver type '{driver_type}' (ROP: {rop_path})")
    parm = rop_node.parm(parm_name)
    if not parm:
        raise hou.NodeError(f"Could not find parameter '{parm_name}' on ROP node {rop_path} (type: {driver_type})")
    return parm.unexpandedString()

@rop_error_handler(error_message="Error checking simulation status")
def is_simulation(input_type):
    """
    Check if a driver type represents a simulation.

    Simulations are not split into frame chunks, and their frame spec UI is hidden.

    Args:
        input_type: Driver type name (e.g., 'dop', 'karma').

    Returns:
        bool: True if the driver type is a simulation, False otherwise.
    """
    return DRIVER_TYPES.get(input_type, DRIVER_TYPES["unknown"])["is_simulation"]

@rop_error_handler(error_message="Error retrieving driver data")
def get_driver_data(node):
    """
    Retrieve the driver data for the connected input node.

    Determines the driver type based on the node type, render delegate, or USD render settings.

    Args:
        node: Conductor Submitter node with a driver_path parameter.

    Returns:
        dict: Driver data from DRIVER_TYPES, or the 'unknown' driver data if no specific
              driver type could be determined.

    Raises:
        hou.NodeError: If an unexpected exception occurs during driver data retrieval.
    """
    driver_type = None
    driver_node_path = node.parm('driver_path').evalAsString()
    driver_node = hou.node(driver_node_path) if driver_node_path else None
    if driver_node:
        driver_type = driver_node.type().name()
    conductor_node_type = rops.get_node_type(node)
    node_list_with_delegate_logic = rops.get_node_list("render_delegate")
    if conductor_node_type in node_list_with_delegate_logic:
        if conductor_node_type in ["husk", "generator", "scheduler"]:
            render_delegate_parm_value = rops.get_parameter_value(node, "render_delegate")
            logger.debug(f"render_delegate_parm_value: {render_delegate_parm_value}")
            if render_delegate_parm_value:
                delegate_key = render_delegate_parm_value.lower()
                if delegate_key in render_delegate_dict:
                    driver_type = render_delegate_dict[delegate_key]
        elif conductor_node_type in ["solaris", "rop"]:
            usd_render_delegate_name = rops.get_render_delegate(node)
            if usd_render_delegate_name:
                usd_render_delegate_name_lower = usd_render_delegate_name.lower()
                for key_in_dict, mapped_driver_type in render_delegate_dict.items():
                    if key_in_dict in usd_render_delegate_name_lower:
                        driver_type = mapped_driver_type
                        break
    return DRIVER_TYPES.get(driver_type, DRIVER_TYPES["unknown"])

@rop_error_handler(error_message="Error retrieving driver node")
def get_driver_node(node):
    """
    Retrieve the connected driver node.

    Args:
        node: Conductor Submitter node with a driver_path parameter.

    Returns:
        hou.Node: The driver node, or None if not found.
    """
    return hou.node(node.parm("driver_path").evalAsString())

@rop_error_handler(error_message="Error updating input node UI")
def update_input_node(node):
    """
    Update the UI when an input connection is made or broken.

    Sets the driver path and type in the UI, and hides frame range override for simulations.
    Also updates render ROP options if connected.

    Args:
        node: Conductor Submitter node with input changes.
    """
    input_nodes = node.inputs()
    connected = input_nodes and input_nodes[0]
    path = input_nodes[0].path() if connected else ""
    node.parm("driver_path").set(path)
    if connected:
        render_rops.add_render_rops(node)

@rop_error_handler(error_message="Error calculating output path")
def calculate_output_path(node):
    """
    Calculate the output directory path for the connected driver node.

    Uses the driver's output parameter or defaults to $HIP/render if not available.

    Args:
        node: Conductor Submitter node with a driver_path parameter.

    Returns:
        str: The output directory path.

    Raises:
        hou.NodeError: If an unexpected exception occurs or path cannot be determined.
    """
    output_folder = None
    driver_node_path = node.parm('driver_path').evalAsString()
    driver_node = hou.node(driver_node_path) if driver_node_path else None
    if driver_node:
        driver_type_from_node = driver_node.type().name()
        if not "usdrender" in driver_type_from_node:
            callback = DRIVER_TYPES.get(driver_type_from_node, DRIVER_TYPES["unknown"])
            parm_name = callback.get("parm_name")
            if parm_name:
                parm = driver_node.parm(parm_name)
                if parm:
                    output_folder = callback["dirname_func"](parm)
        else:
            parm = driver_node.parm("outputimage")
            if parm:
                output_folder = get_single_dirname(parm)
    if not output_folder:
        hip_path = os.path.expandvars("$HIP")
        if os.path.isfile(hip_path) or hip_path == "untitled.hip":
            hip_dir = os.path.dirname(hip_path) if hip_path != "untitled.hip" else "."
        else:
            hip_dir = hip_path
        output_folder = os.path.join(hip_dir, 'render') if hip_dir else 'render'
    if not output_folder or "INVALID FILENAME" in output_folder or "UNKNOWN INPUT" in output_folder:
        raise hou.NodeError(f"Could not determine a valid output path for node '{node.path()}'" +
                           (f". Determined path: '{output_folder}'" if output_folder else ""))
    return output_folder