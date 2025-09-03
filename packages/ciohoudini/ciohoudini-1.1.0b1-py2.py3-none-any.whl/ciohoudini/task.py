"""
Houdini Conductor Task Management

This module provides functions to manage task templates and payload resolution for Conductor
submissions in Houdini. It handles task template formatting, retrieval of node parameters,
and generation of task data for rendering jobs, including support for USD and husk rendering.

Dependencies:
- re: Standard library for regular expressions
- os: Standard library for OS interactions
- ciocore.loggeria: Custom logging for Conductor
- ciohoudini: Custom Houdini utilities (frames, context, rops, util)
"""

import re
import os
import hou
from ciopath.gpath import Path
from ciohoudini import frames, context, rops, util
from ciohoudini.util import rop_error_handler

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

@rop_error_handler(error_message="Error retrieving task template")
def get_task_template(node, **kwargs):
    """
    Retrieves and formats the task template for the node.

    Args:
        node (hou.Node): The Houdini node to generate the task template for.
        **kwargs: Additional keyword arguments including first, last, step, rop_path.

    Returns:
        str: The formatted task template, or empty string on error.
    """
    task_template = ""
    first = kwargs.get("first", 1)
    last = kwargs.get("last", 1)
    step = kwargs.get("step", 1)
    count = last - first + 1
    rop_path = kwargs.get("rop_path", None)
    render_script = node.parm("render_script").eval()
    render_delegate = rops.get_render_delegate(node)
    image_output = get_image_output(node)
    usd_filepath = get_usd_path(node)
    render_scene = get_render_scene(node)
    # set working_dir to be $HIP folder:
    working_dir = os.path.dirname(render_scene)
    working_dir = f'"{working_dir}"'
    script_path = re.sub("^[a-zA-Z]:", "", render_script).replace("\\", "/")
    script_path = f'"{script_path}"'
    if rop_path:
        rop_path = os.path.expandvars(rop_path)
    data = {
        "script": script_path,
        "render_script": script_path,
        "pdg_script": script_path,
        "first": first,
        "last": last,
        "step": step,
        "count": count,
        "driver": rop_path,
        "topnet_path": rop_path,
        "render_rop": rop_path,
        "workitem_index": kwargs["first"],
        "working_dir": working_dir,
        "image_output": image_output,
        "usd_filepath": usd_filepath,
        "render_delegate": render_delegate,
        "hipfile": render_scene,
        "render_scene": render_scene,
        "hserver": ""
    }
    cmd = rops.get_parameter_value(node, "task_template", string_value=True)
    if not cmd:
        logger.debug("Task template is empty, using default task template")
        cmd = rops.get_default_task_template(node, rop_path)
    task_template = cmd.format(**data)
    return task_template

@rop_error_handler(error_message="Error retrieving render scene")
def get_render_scene(node):
    """
    Retrieves the render scene path from the node.

    Args:
        node (hou.Node): The Houdini node to query.

    Returns:
        str: The render scene path, or default if not found.
    """
    render_scene = rops.get_parameter_value(node, "render_scene", string_value=True)
    render_scene = util.prepare_path(render_scene)
    return render_scene

@rop_error_handler(error_message="Error retrieving image output")
def get_image_output(node):
    """
    Retrieves the image output path from the node.

    Args:
        node (hou.Node): The Houdini node to query.

    Returns:
        str: The image output path, or default if not found.
    """
    image_output = None
    node_type = rops.get_node_type(node)
    node_list = rops.get_node_list("import_image_output")
    if node_type in node_list:
        image_output = rops.get_parameter_value(node, "override_image_output", string_value=True)
        image_output = util.prepare_path(image_output)
    image_output = util.prepare_path(image_output)  # Expand Houdini expressions
    return image_output

@rop_error_handler(error_message="Error retrieving USD path")
def get_usd_path(node):
    """
    Retrieves the USD file path from the node using ciopath.

    Args:
        node (hou.Node): The Conductor Submitter node

    Returns:
        str: The USD file path as a forward-slash normalized string, or empty string if not found.
    """
    usd_path = None
    node_type = rops.get_node_type(node)
    node_list = rops.get_node_list("usd_filepath")
    if node_type in node_list:
        raw_usd_path = rops.get_parameter_value(node, "usd_filepath", string_value=True)
        if raw_usd_path:
            usd_path = util.prepare_path(raw_usd_path)
    return usd_path

@rop_error_handler(error_message="Error resolving task payload")
def resolve_payload_original(node, **kwargs):
    """
    Resolves the task_data field for the submission payload.

    In simulation mode, emits a single task. Otherwise, generates tasks based on frame chunks.

    Args:
        node (hou.Node): The Houdini node to generate tasks for.
        **kwargs: Additional keyword arguments including task_limit, frame_range.

    Returns:
        dict: A dictionary with the tasks_data field containing task commands and frames.
    """
    tasks = []
    if not node:
        return {"tasks_data": tasks}
    task_limit = kwargs.get("task_limit", -1)
    frame_range = kwargs.get("frame_range", None)
    if node.parm("is_sim").eval():
        cmd = node.parm("task_template").eval()
        tasks = [{"command": cmd, "frames": "0"}]
        return {"tasks_data": tasks}
    resolved_chunk_size = frames.get_resolved_chunk_size(node, frame_range=frame_range)
    sequence = frames.main_frame_sequence(node, frame_range=frame_range, resolved_chunk_size=resolved_chunk_size)
    chunks = sequence.chunks()
    for i, chunk in enumerate(chunks):
        if task_limit > -1 and i >= task_limit:
            break
        kwargs["first"] = chunk.start
        kwargs["last"] = chunk.end
        kwargs["step"] = chunk.step
        logger.debug("resolve_payload: kwargs: {}".format(kwargs))
        cmd = get_task_template(node, **kwargs)
        context.set_for_task(first=chunk.start, last=chunk.end, step=chunk.step)
        tasks.append({"command": cmd, "frames": str(chunk)})
    return {"tasks_data": tasks}


@rop_error_handler(error_message="Error resolving task payload")
def resolve_payload(node, **kwargs):
    """
    Resolves the task_data field for the submission payload.

    In simulation mode, emits a single task. Otherwise, generates tasks based on frame chunks.

    Args:
        node (hou.Node): The Houdini node to generate tasks for.
        **kwargs: Additional keyword arguments including task_limit, frame_range.

    Returns:
        dict: A dictionary with the tasks_data field containing task commands and frames.
    """
    tasks = []
    if not node:
        return {"tasks_data": tasks}
    task_limit = kwargs.get("task_limit", -1)
    frame_range = kwargs.get("frame_range", None)
    if node.parm("is_sim").eval():
        cmd = node.parm("task_template").eval()
        tasks = [{"command": cmd, "frames": "0"}]
        return {"tasks_data": tasks}
    resolved_chunk_size = frames.get_resolved_chunk_size(node, frame_range=frame_range)
    sequence = frames.main_frame_sequence(node, frame_range=frame_range, resolved_chunk_size=resolved_chunk_size)
    chunks = sequence.chunks()
    for i, chunk in enumerate(chunks):
        if task_limit > -1 and i >= task_limit:
            break
        # These assignments modify the kwargs dictionary that was passed in,
        # or add new keys if they weren't present.
        kwargs["first"] = chunk.start
        kwargs["last"] = chunk.end
        kwargs["step"] = chunk.step
        kwargs["chunk"] = chunk

        # Create a safe version of kwargs for logging to prevent ObjectWasDeleted errors
        kwargs_for_logging = {}
        for key, value in kwargs.items():
            if isinstance(value, (hou.Parm, hou.ParmTuple)):
                try:
                    # Test if repr(value) would succeed. This is what .format() does.
                    # If this line doesn't raise an error, the object is safe to log.
                    repr(value)
                    kwargs_for_logging[key] = value
                except hou.ObjectWasDeleted:
                    kwargs_for_logging[key] = f"<deleted {type(value).__name__}>"
            else:
                kwargs_for_logging[key] = value

        logger.debug("resolve_payload: kwargs: {}".format(kwargs_for_logging))  # Use the sanitized version for logging

        # The original kwargs (which might contain live hou.Node or other objects)
        # is still passed to get_task_template.
        cmd = get_task_template(node, **kwargs)
        context.set_for_task(first=chunk.start, last=chunk.end, step=chunk.step)
        tasks.append({"command": cmd, "frames": str(chunk)})
    return {"tasks_data": tasks}