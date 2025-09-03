"""
Houdini Conductor Submission Handler

This module handles submission and testing of jobs to Conductor from Houdini. It provides
functionality to open a submission dialog, submit jobs, generate submission payloads,
and export submission scripts for manual execution.

Dependencies:
- os: Standard library for OS interactions
- traceback: Standard library for exception handling
- json: Standard library for JSON handling
- hou: Houdini Python module
- ciocore: Core Conductor utilities (conductor_submit, loggeria)
- ciohoudini: Custom Houdini utilities (payload, rops, submission_dialog)
- contextlib: Standard library for context managers
"""

import os
import traceback
import json
import hou
from ciohoudini import payload, rops
from contextlib import contextmanager
from ciocore import conductor_submit
from ciohoudini.submission_dialog import SubmissionDialog

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

# Define success codes for API responses
SUCCESS_CODES = [201, 204]

# Get CIODIR environment variable for ciocore package path
CIODIR = os.environ.get("CIODIR")

@contextmanager
def saved_scene(node=None):
    """
    Context manager to ensure the scene is saved before submission.

    Saves the scene if modified, autosave is enabled, or HDAs need embedding.
    Yields the scene filename.

    Args:
        node (hou.Node, optional): The Houdini node with submission parameters.

    Yields:
        str: The filename of the saved scene, or current scene if no save is needed.
    """
    current_scene_name = hou.hipFile.name()
    always_use_autosave = node and node.parm("use_autosave").eval()
    modified = hou.hipFile.hasUnsavedChanges()
    should_embed_hdas = node and node.parm("embed_hdas").eval()
    orig_embed_hdas_val = _get_save_op_defs()

    try:
        fn = None
        if modified or always_use_autosave or should_embed_hdas:
            if should_embed_hdas:
                _set_save_op_defs(True)
            fn = node.parm("autosave_scene").eval()
            hou.hipFile.save(file_name=fn, save_to_recent_files=False)
        else:
            fn = hou.hipFile.path()
            hou.findFile(fn)  # Raises if file is deleted
        yield fn
    finally:
        _set_save_op_defs(orig_embed_hdas_val)
        hou.hipFile.setName(current_scene_name)

def _get_save_op_defs():
    """
    Retrieves the current state of the 'Save Operator Definitions' setting.

    Returns:
        bool: True if operator definitions are saved, False otherwise.
    """
    otconfig = hou.hscript("otconfig")
    result = next(f for f in otconfig[0].split("\n") if f.startswith("Save Operator Definitions"))
    result = result.split(":")[1].strip()
    return result == "true"

def _set_save_op_defs(state):
    """
    Sets the 'Save Operator Definitions' setting for embedding HDAs.

    Args:
        state (bool): True to enable saving operator definitions, False to disable.
    """
    val = 1 if state else 0
    hou.hscript(f"otconfig -s {val}")

def invoke_submission_dialog(*nodes, **kwargs):
    """
    Opens a modal submission dialog for the given nodes.

    Args:
        *nodes: Variable number of Houdini nodes to process.
        **kwargs: Additional keyword arguments (not used in current implementation).
    """
    submission_dialog = SubmissionDialog(nodes)
    hou.session.conductor_validation = submission_dialog
    submission_dialog.show()  # Non-modal dialog

def run(node):
    """
    Submits jobs for the given node, saving the scene if necessary.

    Args:
        node (hou.Node): The Houdini node to submit.

    Returns:
        list: List of submission responses, or empty list if submission fails.
    """
    result = []
    if not node:
        return result
    with saved_scene(node) as fn:
        if not fn:
            return result
        return submit_one(node)

def get_submission_payload(node):
    """
    Generates the submission payload for the given node.

    Args:
        node (hou.Node): The Houdini node to generate the payload for.

    Returns:
        list: List of payload dictionaries for submission.
    """
    kwargs = {
        "do_asset_scan": True,
        "task_limit": -1
    }
    submission_payload = payload.resolve_payloads(node, **kwargs)
    return submission_payload

def submit_one(node):
    """
    Submits a single node's payloads to Conductor.

    Args:
        node (hou.Node): The Houdini node to submit.

    Returns:
        list: List of unique submission responses.
    """
    response_list = []
    payloads = get_submission_payload(node)
    job_count = len(payloads)

    if job_count == 0:
        logger.debug("There are no jobs to submit")
        return response_list

    for payload in payloads:
        try:
            remote_job = conductor_submit.Submit(payload)
            response, response_code = remote_job.main()
        except:
            response = traceback.format_exc()
        logger.debug(f"response: {response}")
        if response and response not in response_list:
            response_list.append(response)

    return response_list

SCRIPT_TEMPLATE = '''
""" Conductor Submission Script, auto-generated by the Conductor-for-Houdini submitter. 

NOTE: No validations were carried out during the creation of this script. Conductor cannot be held
responsible for problems or unwanted costs incurred as a result of settings in this script. 

You are advised to always use scout frames, and to keep an eye on the Conductor Dashboard once you
submit this job.

USAGE:
To run this script, enter: `python "{0}"` in a terminal or cmd prompt.
You'll need the ciocore Python package. 
You can install it with pip, (preferably in a virtualenv) `pip install ciocore`. 
Alternatively, add the location of the ciocore package that comes with this submitter to your PYTHONPATH environment variable: `PYTHONPATH="{2}"`.
"""



import sys
import json
from ciocore import conductor_submit

SUBMISSION = """\n
{1}
"""\n

data = json.loads(SUBMISSION)

submission = conductor_submit.Submit(data)
response, response_code = submission.main()
print(response_code)
print(json.dumps(response))

'''

def export_script(node, **kwargs):
    """
    Exports a Python script for manual submission of the node's payload.

    Args:
        node (hou.Node): The Houdini node to generate the script for.
        **kwargs: Additional keyword arguments (not used in current implementation).
    """
    payload_data = get_submission_payload(node)
    destination = hou.ui.selectFile(
        title="Script path to export",
        start_directory=os.path.join(hou.getenv("HIP"), "scripts"),
        file_type=hou.fileType.Any,
        multiple_select=False,
        default_value=os.path.basename("submission.py"),
        chooser_mode=hou.fileChooserMode.Write,
    )
    if not destination:
        logger.debug("No script file selected")
        return

    with open(destination, "w") as f:
        content = SCRIPT_TEMPLATE.format(destination, json.dumps(payload_data, indent=2), CIODIR)
        f.write(content)

    details = """
To run this script, enter: `python "{0}"` in a terminal or cmd prompt.
You'll need the ciocore Python package. 
You can install it with pip, (preferably in a virtualenv) `pip install ciocore`. 
Alternatively, add the location of the ciocore package that comes with this submitter to your PYTHONPATH environment variable: 
`PYTHONPATH="{1}"`.
""".format(destination, CIODIR)

    # Display success message with instructions
    hou.ui.displayMessage(
        title="Export Script Success",
        text=f"Python script exported to '{destination}'",
        details_label="Show instructions",
        details=details,
        severity=hou.severityType.Message,
    )