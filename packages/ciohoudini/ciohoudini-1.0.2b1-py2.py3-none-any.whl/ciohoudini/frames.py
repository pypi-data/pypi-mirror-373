"""
Module for managing frame ranges and sequences in the Conductor plugin for Houdini.

This module handles frame range retrieval from various sources (playbar, ROP nodes, custom settings),
updates UI elements, and generates frame sequences for rendering, including scout frame calculations
for submission payloads.
"""

import hou
import re
import math

# Set expression language to Python
XPY = hou.exprLanguage.Python
from ciohoudini import errors, rops, util
from ciohoudini.util import rop_error_handler
from cioseq.sequence import Sequence
from ciocore import data as coredata

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

# Regular expressions for parsing scout frame specifications
AUTO_RX = re.compile(r"^auto[, :]+(\d+)$")  # Matches 'auto:5' or 'auto,5'
FML_RX = re.compile(r"^fml[, :]+(\d+)$")    # Matches 'fml:3' or 'fml,3'

# Maximum number of tasks allowed for chunking
MAX_TASKS = 800

# Expression to dynamically set frame range based on ROP or playbar
EXPR = """
import hou
from cioseq.sequence import Sequence

rop = hou.node(hou.pwd().parm('driver_path').evalAsString())
if not rop:
    first, last = hou.playbar.timelineRange()
    inc = hou.playbar.frameIncrement()
    return str(Sequence.create( first, last, inc))

use_range = rop.parm("trange").eval()
if not use_range:
    return int(hou.frame())

progression = rop.parmTuple("f").eval()
return str(Sequence.create(*progression))
"""

@rop_error_handler(error_message="Error toggling custom frame range")
def on_use_custom(node, **kwargs):
    """
    Toggle custom frame range override for the node.

    Removes keyframes and sets a Python expression for frame range when custom frames are disabled.

    Args:
        node: Conductor Submitter node to configure.
        **kwargs: Additional arguments (unused).
    """
    node.parm("frame_range").deleteAllKeyframes()
    if not node.parm("use_custom_frames").eval():
        node.parm("frame_range").setExpression(EXPR, XPY, True)

@rop_error_handler(error_message="Error populating frame range menu")
def populate_frame_range_menu(node):
    """
    Populate the frame range source menu in the UI.

    Returns a flat list of menu options for the frame range source dropdown.

    Args:
        node: Conductor Submitter node containing the frame range source parameter.

    Returns:
        list: Flattened list of menu items (label, value pairs).
    """
    frame_override_methods = ["Houdini playbar", "Render rop node"]
    return [el for i in frame_override_methods for el in (i, i)]

@rop_error_handler(error_message="Error updating render ROP frame range")
def update_render_rop_frame_range(node):
    """
    Update frame ranges for all render ROPs listed in the node's UI.

    Retrieves frame ranges for each ROP and sets corresponding UI parameters.

    Args:
        node: Conductor Submitter node containing render ROP parameters.
        **kwargs: Additional arguments (unused).
    """
    node_type = rops.get_node_type(node)
    if node_type not in ["scheduler"]:
        render_rops_parm = node.parm("render_rops")
        if render_rops_parm:
            curr_count = render_rops_parm.eval()
            for i in range(1, curr_count + 1):
                rop_path_parm = node.parm(f"rop_path_{i}")
                if rop_path_parm:
                    rop_path = rop_path_parm.evalAsString()
                    frame_range = get_all_rop_frame_range(node, rop_path)
                    if frame_range:
                        rop_frame_range_parm = node.parm(f"rop_frame_range_{i}")
                        if rop_frame_range_parm:
                            rop_frame_range_parm.set(frame_range)

@rop_error_handler(error_message="Error setting default frame range")
def set_default_frame_range(node, **kwargs):
    """
    Set the default frame range based on the Houdini playbar.

    Args:
        node: Conductor Submitter node to set the frame range for.
        **kwargs: Additional arguments (unused).
    """
    node_type = rops.get_node_type(node)
    if node_type not in ["scheduler"]:
        frame_range = get_playbar_frame_range(node, None)
        rops.set_parameter_value(node, "frame_range", frame_range)

@rop_error_handler(error_message="Error updating frame range")
def update_frame_range(node, **kwargs):
    """
    Update the frame range for the node based on its type.

    Specifically updates render ROP frame ranges for 'job' node types.

    Args:
        node: Conductor Submitter node to update.
        **kwargs: Additional arguments passed to update_render_rop_frame_range.
    """
    node_type = rops.get_node_type(node)
    if node_type in ["generator"]:
        update_render_rop_frame_range(node)

@rop_error_handler(error_message="Error retrieving playbar frame range")
def get_sequence_playbar_frame_range(node, rop):
    """
    Retrieve the frame range from the Houdini playbar.

    Args:
        node: Conductor Submitter node (unused, for consistency).
        rop: Render ROP node (unused, for consistency).

    Returns:
        str: Frame range in the format 'start-end' (e.g., '1-100').
    """
    return Sequence(hou.playbar.playbackRange())

@rop_error_handler(error_message="Error retrieving playbar frame range")
def get_playbar_frame_range(node, rop):
    """ Get the frame range from the Houdini playbar."""
    start_time, end_time = hou.playbar.playbackRange()
    frame_range = "{}-{}".format(int(start_time), int(end_time))
    return frame_range

@rop_error_handler(error_message="Error retrieving custom frame range")
def get_custom_frame_range(node, rop):
    """
    Retrieve the custom frame range from the node's frame_range parameter.

    Args:
        node: Conductor Submitter node containing the frame range parameter.
        rop: Render ROP node (unused, for consistency).

    Returns:
        str: Custom frame range string.
    """
    return node.parm("frame_range").eval()

@rop_error_handler(error_message="Error retrieving ROP frame range")
def get_rop_frame_range(node, rop):
    """
    Retrieve the frame range from a render ROP node.

    Args:
        node: Conductor Submitter node (unused, for consistency).
        rop: Path to the render ROP node.

    Returns:
        str: Frame range in the format 'start-end' or '1' if the ROP is invalid.
    """
    frame_range = "1"
    node_type = rops.get_node_type(node)
    if node_type not in ["scheduler"]:
        rop_node = hou.node(rop)
        if rop_node:
            frame_range = f"{int(rop_node.parm('f1').eval())}-{int(rop_node.parm('f2').eval())}"
    return frame_range

@rop_error_handler(error_message="Error retrieving all ROP frame range")
def get_all_rop_frame_range(node, rop_path):
    """
    Retrieve the frame range for a ROP based on the selected frame range source.

    Args:
        node: Conductor Submitter node containing the frame range source parameter.
        rop_path: Path to the render ROP node.

    Returns:
        str: Frame range in the format 'start-end' or '1' for invalid sources.
    """
    frame_range = "1"
    node_type = rops.get_node_type(node)
    if node_type not in ["scheduler"]:
        menu_value = node.parm("frame_range_source").eval()
        if menu_value == "Houdini playbar":
            frame_range = get_playbar_frame_range(node, rop_path)
        elif menu_value == "Render rop node":
            frame_range = get_rop_frame_range(node, rop_path)
        elif menu_value == "Custom frame range":
            frame_range = get_custom_frame_range(node, rop_path)
        else:
            frame_range = "1"
    return frame_range

@rop_error_handler(error_message="Error updating stats panel")
def set_stats_panel(node, **kwargs):
    """
    Update the stats panel with frame-related statistics.

    Calculates frame counts, task counts, and scout frame specifications for display.

    Args:
        node: Conductor Submitter node containing frame and stats parameters.
        **kwargs: Additional arguments (unused).
    """
    if node.parm("is_sim").eval():
        node.parm("scout_frame_spec").set("0")
        node.parmTuple("frame_task_count").set((1, 1))
        node.parmTuple("scout_frame_task_count").set((0, 0))
        return
    main_seq = main_frame_sequence(node)
    frame_count = len(main_seq)
    task_count = main_seq.chunk_count()
    chunk_size = node.parm("chunk_size").eval()
    node.parm("resolved_chunk_size").set(str(chunk_size))
    resolved_chunk_size = cap_chunk_count(task_count, frame_count, chunk_size)
    if resolved_chunk_size >= chunk_size:
        node.parm("resolved_chunk_size").set(str(resolved_chunk_size))
        main_seq = main_frame_sequence(node, resolved_chunk_size=resolved_chunk_size)
        task_count = main_seq.chunk_count()
        frame_count = len(main_seq)
    scout_seq = scout_frame_sequence(node, main_seq)
    scout_frame_count = frame_count
    scout_task_count = task_count
    scout_frame_spec = "No scout frames. All frames will be started."
    if scout_seq:
        scout_chunks = main_seq.intersecting_chunks(scout_seq)
        if scout_chunks:
            scout_tasks_sequence = Sequence.create(",".join(str(chunk) for chunk in scout_chunks))
            scout_frame_count = len(scout_tasks_sequence)
            scout_task_count = len(scout_chunks)
            scout_frame_spec = str(scout_seq)
    node.parm("scout_frame_spec").set(scout_frame_spec)
    node.parmTuple("frame_task_count").set((frame_count, task_count))
    node.parmTuple("scout_frame_task_count").set((scout_frame_count, scout_task_count))

@rop_error_handler(error_message="Error calculating resolved chunk size")
def get_resolved_chunk_size(node, frame_range=None):
    """
    Calculate the resolved chunk size for the node's frame sequence.

    Adjusts the chunk size to respect the maximum task count.

    Args:
        node: Conductor Submitter node containing frame range and chunk size parameters.
        frame_range: Optional frame range string to override node parameter.

    Returns:
        int: The resolved chunk size.
    """
    main_seq = main_frame_sequence(node, frame_range=frame_range)
    frame_count = len(main_seq)
    task_count = main_seq.chunk_count()
    chunk_size = node.parm("chunk_size").eval()
    node.parm("resolved_chunk_size").set(str(chunk_size))
    resolved_chunk_size = cap_chunk_count(task_count, frame_count, chunk_size)
    if resolved_chunk_size >= chunk_size:
        node.parm("resolved_chunk_size").set(str(resolved_chunk_size))
        return resolved_chunk_size
    return chunk_size

@rop_error_handler(error_message="Error capping chunk count")
def cap_chunk_count(task_count, frame_count, chunk_size):
    """
    Cap the number of tasks to a maximum value to limit render farm load.

    Args:
        task_count: Current number of tasks.
        frame_count: Total number of frames.
        chunk_size: Desired chunk size.

    Returns:
        int: Adjusted chunk size to cap tasks at MAX_TASKS.
    """
    if task_count > MAX_TASKS:
        return math.ceil(frame_count / MAX_TASKS)
    return chunk_size

@rop_error_handler(error_message="Error generating main frame sequence", warning_only=True)
def main_frame_sequence(node, frame_range=None, resolved_chunk_size=None):
    """
    Generate a Sequence object for the node's chosen frame range.

    Args:
        node: Conductor Submitter node containing frame range and chunk size parameters.
        frame_range: Optional frame range string to override node parameter.
        resolved_chunk_size: Optional resolved chunk size to override node parameter.

    Returns:
        Sequence: The frame sequence object.
    """
    if not resolved_chunk_size:
        chunk_size = node.parm("chunk_size").eval()
    else:
        chunk_size = resolved_chunk_size
    if frame_range:
        spec = frame_range
    else:
        spec = node.parm("frame_range").eval()
    with errors.show():
        return Sequence.create(spec, chunk_size=chunk_size, chunk_strategy="progressions")

@rop_error_handler(error_message="Error generating scout frame sequence")
def scout_frame_sequence(node, main_sequence):
    """
    Generate a Sequence object for scout frames based on the node's settings.

    Supports auto-subsampling, FML (first-middle-last), or custom scout frame specifications.

    Args:
        node: Conductor Submitter node containing scout frame parameters.
        main_sequence: Main frame sequence to intersect with scout frames.

    Returns:
        Sequence: The scout frame sequence, or None if disabled or invalid.
    """
    if not node.parm("use_scout_frames").eval():
        return
    scout_spec = node.parm("scout_frames").eval()
    match = AUTO_RX.match(scout_spec)
    if match:
        samples = int(match.group(1))
        return main_sequence.subsample(samples)
    else:
        match = FML_RX.match(scout_spec)
        if match:
            samples = int(match.group(1))
            return main_sequence.calc_fml(samples)
    return Sequence.create(scout_spec).intersection(main_sequence)

@rop_error_handler(error_message="Error resolving scout frames payload")
def resolve_payload(node, frame_range=None):
    """
    Generate the scout frames portion of the submission payload.

    Excludes scout frames for simulations or if disabled.

    Args:
        node: Conductor Submitter node containing frame range and scout frame parameters.
        frame_range: Optional frame range string to override node parameter.

    Returns:
        dict: Dictionary containing scout frames, or empty dict if none.
    """
    if rops.get_parameter_value(node, "is_sim"):
        return {}
    if not rops.get_parameter_value(node, "use_scout_frames"):
        return {}
    main_seq = main_frame_sequence(node, frame_range=frame_range)
    scout_sequence = scout_frame_sequence(node, main_seq)
    if scout_sequence:
        return {"scout_frames": ",".join([str(f) for f in scout_sequence])}
    return {}