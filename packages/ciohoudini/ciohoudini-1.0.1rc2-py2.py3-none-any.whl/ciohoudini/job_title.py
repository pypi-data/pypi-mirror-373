"""
Module for managing the job title in the Conductor plugin for Houdini.

This module handles the generation of the job title for the submission payload,
optionally appending a render ROP path to the user-defined title.
"""

import hou


def resolve_payload(node, rop_path=None):
    """
    Generate the job title portion of the submission payload.

    Retrieves the title from the node's UI parameter and optionally appends the ROP path.

    Args:
        node: Conductor Submitter node containing the title parameter.
        rop_path: Optional path to the render ROP to append to the title (default: None).

    Returns:
        dict: Dictionary containing the job title.
    """
    # Get the user-defined title and remove leading/trailing whitespace
    title = node.parm("title").eval().strip()
    # Append ROP path if provided
    if rop_path:
        title = f"{title}  {rop_path}"
    # Return payload dictionary
    return {"job_title": title}
