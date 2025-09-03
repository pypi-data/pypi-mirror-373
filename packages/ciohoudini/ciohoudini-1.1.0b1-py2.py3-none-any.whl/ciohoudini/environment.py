"""
Module for managing environment variables in the Conductor plugin for Houdini.

This module handles the creation and manipulation of environment variables for the Conductor
submission payload, including package-based variables, extra user-defined variables, and
UI interactions for adding or removing variables.
"""

import os
import re
import hou
from ciohoudini import software
from ciopath.gpath_list import PathList
from ciopath.gpath import Path
import sys
from ciocore.package_environment import PackageEnvironment

# Regular expression to identify drive letters in paths (e.g., "C:")
DRIVE_LETTER_RX = re.compile(r"^[a-zA-Z]:")


def resolve_payload(node):
    """
    Build the environment section of the payload for a given Houdini node.

    Combines environment variables from packages and extra user-defined variables,
    handling merge policies (append or exclusive) and ensuring compatibility with Conductor.

    Args:
        node: Conductor Submitter node containing environment parameters.

    Returns:
        dict: A dictionary with an 'environment' key mapping to the resolved environment variables.
    """
    pkg_env = PackageEnvironment()

    # Add environment variables from software packages
    for package in software.packages_in_use(node):
        pkg_env.extend(package)

    # Add Conductor-specific environment variable
    pkg_env.extend(
        [{"name": "CONDUCTOR_PATHHELPER", "value": "0", "merge_policy": "exclusive"}]
    )

    # Determine Houdini host version for compatibility settings
    try:
        host_version = int(node.parm("host_version").eval().split()[1].split(".")[0])
    except:
        host_version = 19

    # Set Houdini server HTTP usage based on version
    if host_version < 19:
        pkg_env.extend(
            [{"name": "HOUDINI_HSERVER_USE_HTTP", "value": "2", "merge_policy": "exclusive"}]
        )
    else:
        pkg_env.extend(
            [{"name": "HOUDINI_HSERVER_USE_HTTP", "value": "0", "merge_policy": "exclusive"}]
        )

    # Add JOB environment variable with normalized path
    pkg_env.extend(
        [{
            "name": "JOB",
            "value": Path(hou.getenv("JOB")).fslash(with_drive=False),
            "merge_policy": "exclusive"
        }]
    )

    # Add OCIO environment variable if defined
    ocio_file = os.environ.get("OCIO")
    if ocio_file:
        pkg_env.extend(
            [{"name": "OCIO", "value": Path(ocio_file).fslash(with_drive=False), "merge_policy": "exclusive"}]
        )

    # Process extra user-defined environment variables
    extra_env = get_extra_env(node)
    for i, entry in enumerate(extra_env):
        policy = entry["merge_policy"]
        index = i + 1
        try:
            pkg_env.extend([entry])
        except ValueError:
            excl_parm = node.parm("env_excl_{}".format(index))
            excl_parm.set(not excl_parm.eval())
            entry["merge_policy"] = ["append", "exclusive"][excl_parm.eval()]
            pkg_env.extend([entry])

    return {"environment": dict(pkg_env)}


def get_extra_env(node):
    """Get a list of extra env vars from the UI.

    The items also have a merge_policy flag, which is used
    in compiling the final environment that will be sent to
    Conductor.
    """
    num = node.parm("environment_kv_pairs").eval()
    result = []
    for i in range(1, num + 1):
        is_exclusive = node.parm("env_excl_{:d}".format(i)).eval()
        name = node.parm("env_key_{:d}".format(i)).eval()
        value = node.parm("env_value_{:d}".format(i)).eval()
        if name and value:
            result.append(
                {
                    "name": node.parm("env_key_{:d}".format(i)).eval(),
                    "value": node.parm("env_value_{:d}".format(i)).eval(),
                    "merge_policy": ["append", "exclusive"][is_exclusive],
                }
            )
    return result


def add_variable(node, **kwargs):
    """Add a new variable to the UI.

    This is called by the UI when the user clicks the Add Variable button.

    It can also be called programatically by using the variable keyword, which should contain a tuple:
    key e.g. PATH
    value: e.g. /usr/julian/bin
    is_exclusive: e.g. False

    """
    key, value, is_exclusive = kwargs.get("variable", ("", "", False))

    next_index = node.parm("environment_kv_pairs").eval() + 1
    if not (key and value):
        # Add an empty line for the user to fill in.
        node.parm("environment_kv_pairs").set(next_index)
        return

    existing_env = get_extra_env(node)
    exists = False
    for entry in existing_env:
        if entry["name"] == key and entry["value"] == value:
            exists = True
            break
    if not exists:
        node.parm("environment_kv_pairs").set(next_index)
        node.parm("env_key_{}".format(next_index)).set(key)
        node.parm("env_value_{}".format(next_index)).set(value)
        node.parm("env_excl_{}".format(next_index)).set(is_exclusive)


def remove_variable(node, index):
    """Remove a variable from the UI.

    Remove the entry at the given index and shift all subsequent entries down.
    """
    curr_count = node.parm("environment_kv_pairs").eval()
    for i in range(index + 1, curr_count + 1):
        for parm_name in ["key", "value", "excl"]:
            from_parm = node.parm("env_{}_{}".format(parm_name, i))
            to_parm = node.parm("env_{}_{}".format(parm_name, i - 1))
            try:
                to_parm.set(from_parm.rawValue())
            except TypeError:
                to_parm.set(from_parm.evalAsInt())
    node.parm("environment_kv_pairs").set(curr_count - 1)


def add_existing_variables(node, **kwargs):
    """Convenience function to add existing environment variables.

    This is called by the UI when the user clicks the Add Existing Variable button.

    It can also be called programatically by using the variables keyword (NOTE THE PLURAL), which should contain a list of env var names.

    Args:
        variables: List of strings 
        E.g. ["HISTTIMEFORMAT", "CUDA_CACHE_MAXSIZE", "VRAY_FOR_MAYA2022_PLUGINS"]

    If the variables keyword arg is not given, the user will be prompted to select variables from a list.

    On adding variables, we guess their exclusive status based on the count when split with the os.separator.

    We don 't add variables from the Houdini installation.

    """
    blacklist = (os.environ["HFS"],)

    variables = kwargs.get("variables", None)
    if not variables:
        variables = sorted([k for k in os.environ])
        results = hou.ui.selectFromList(
            variables,
            exclusive=False,
            message="Select variables to be set remotely",
            title="Add existing variables",
            column_header="Choices",
            num_visible_rows=15,
            clear_on_cancel=False,
            width=0,
            height=0)

        variables = [n for i,n in enumerate(variables) if i in results]

    for variable in variables:

        values = [p for p in os.environ[variable].split(os.pathsep) if p]
        exclusive =  len(values) == 1
        for value in values:
            if value.startswith(blacklist):
                continue
            if DRIVE_LETTER_RX.match(value):
                value = Path(value).fslash(with_drive=False)
            
            add_variable(node, variable=(variable, value, exclusive))
 
