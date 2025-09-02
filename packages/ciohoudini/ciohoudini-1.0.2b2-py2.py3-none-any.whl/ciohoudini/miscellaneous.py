"""
Module for handling miscellaneous payload fields and utility functions in the Conductor plugin for Houdini.

This module manages notification emails, location tags, local upload settings, render script copying,
and log level changes for the Conductor submission process.
"""

import os
import re
import shutil

import hou

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

# Regular expression for basic email validation
SIMPLE_EMAIL_RE = re.compile(r"^\S+@\S+$")


def resolve_payload(node, **kwargs):
    """
    Generate miscellaneous fields for the submission payload.

    Includes notification email addresses, location tags, and local upload settings.

    Args:
        node: Conductor Submitter node containing payload parameters.
        **kwargs: Additional arguments (unused).

    Returns:
        dict: Dictionary with notify, location, and local_upload fields as applicable.
    """
    result = {}
    # Add notification email addresses if any
    addresses = resolve_email_addresses(node)
    if addresses:
        result["notify"] = addresses
    # Add location tag if specified
    location = resolve_location(node)
    if location:
        result["location"] = location

    # Set local upload based on daemon usage
    result["local_upload"] = not node.parm("use_daemon").eval()
    return result


def resolve_email_addresses(node):
    """
    Retrieve and validate email addresses for notifications.

    Extracts email addresses from the node's UI parameter if email notifications are enabled.

    Args:
        node: Conductor Submitter node containing email notification parameters.

    Returns:
        list: List of validated email addresses, or empty list if disabled or invalid.
    """
    # Return empty list if email notifications are disabled
    if not node.parm("do_email").eval():
        return []

    # Split and validate email addresses
    addresses = node.parm("email_addresses").eval() or ""
    addresses = [a.strip() for a in re.split(', ', addresses) if a and SIMPLE_EMAIL_RE.match(a)]
    return addresses


def resolve_location(node):
    """
    Retrieve the location tag for the submission payload.

    Args:
        node: Conductor Submitter node containing the location tag parameter.

    Returns:
        str: The location tag, or empty string if not set.
    """
    location = node.parm("location_tag").eval()
    return location


def copy_render_script(node, **kwargs):
    """
    Copy the render script to a user-specified destination.

    Updates the node's render script parameter to point to the new location.

    Args:
        node: Conductor Submitter node containing the render script parameter.
        **kwargs: Additional arguments (unused).
    """
    # Get the current render script path
    script = node.parm("render_script").eval()
    if not script:
        logger.debug("Couldn't copy script. No script specified.")
        return

    # Prompt user for destination file
    destination = hou.ui.selectFile(
        title="Destination file",
        start_directory=os.path.join(hou.getenv("HIP"), "scripts"),
        file_type=hou.fileType.Any,
        multiple_select=False,
        default_value=os.path.basename(script),
        chooser_mode=hou.fileChooserMode.Write,
    )

    if not destination:
        logger.debug("Couldn't copy script. No destination specified.")
        return

    # Copy the script to the destination
    shutil.copyfile(script, destination)

    # Update the render script parameter while preserving lock state
    lockstate = node.parm("render_script").isLocked()
    node.parm("render_script").lock(False)
    node.parm("render_script").set(destination)
    node.parm("render_script").lock(lockstate)


def change_log_level(node, **kwargs):
    """
    Change the logging level for the Conductor plugin.

    Args:
        node: Conductor Submitter node (unused, for consistency).
        **kwargs: Additional arguments, including:
            - script_value: The new log level to set.
    """
    ciocore.loggeria.set_conductor_log_level(kwargs['script_value'])