"""
Houdini Conductor Software Management

This module manages three software categories for Conductor submissions in Houdini:
1. Remote Houdini version selection.
2. Plugin selection for the connected driver.
3. Extra plugins for additional functionality.

Dependencies:
- hou: Houdini Python module
- ciocore: Core data utilities (data, loggeria)
- ciohoudini: Custom Houdini utilities (driver, rops)
"""
import re
import hou
from ciocore import data as coredata
from ciohoudini import driver, rops
from ciohoudini.util import rop_error_handler

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

@rop_error_handler(error_message="Error calculating version distance")
def version_distance_2(host, current_version_parts):
    """
    Calculates the numerical distance between the current Houdini version and a host version.

    Args:
        host (str): A host name string from the host_names list (e.g., "houdini 20.5.370.gcc9.3 linux").
        current_version_parts (list): List of integers representing the current version [major, minor, build].

    Returns:
        float: A numerical distance value (lower is better), or float('inf') on parsing error.
    """
    host_version = host.split(" ")[1].split(".gcc")[0]  # Extract "20.5.370"
    host_version_parts = list(map(int, host_version.split(".")))  # Example: [20, 5, 370]
    major_diff = abs(current_version_parts[0] - host_version_parts[0]) * 1000000
    minor_diff = abs(current_version_parts[1] - host_version_parts[1]) * 1000
    build_diff = abs(current_version_parts[2] - host_version_parts[2])
    total_distance = major_diff + minor_diff + build_diff
    return total_distance


@rop_error_handler(error_message="Error calculating version distance")
def version_distance(host, current_version_parts):
    """
    Calculates the numerical distance between the current Houdini version and a host version.

    Args:
        host (str): A host name string from the host_names list (e.g., "houdini 20.5.370.gcc9.3 linux").
        current_version_parts (list): List of integers representing the current version [major, minor, build].

    Returns:
        float: A numerical distance value (lower is better), or float('inf') on parsing error.
    """
    try:
        # Extract the version string part (e.g., "20.5.370" or "19.0.123")
        match = re.search(r'(\d+\.\d+\.\d+)', host)
        if not match:
            logger.warning(f"Could not parse version from host string: {host}")
            return float('inf')

        host_version_str = match.group(1)
        host_version_parts = list(map(int, host_version_str.split(".")))

        if len(host_version_parts) < 3 or len(current_version_parts) < 3:
            logger.warning(
                f"Version parts length mismatch. Host: {host_version_parts}, Current: {current_version_parts} for host string: {host}")
            return float('inf')

        major_diff = abs(current_version_parts[0] - host_version_parts[0]) * 1000000
        minor_diff = abs(current_version_parts[1] - host_version_parts[1]) * 1000
        build_diff = abs(current_version_parts[2] - host_version_parts[2])
        total_distance = major_diff + minor_diff + build_diff
        return total_distance
    except ValueError as e:
        logger.warning(f"ValueError parsing version parts for host '{host}': {e}")
        return float('inf')
    except Exception as e:  # Catch any other unexpected errors during parsing
        logger.error(f"Unexpected error in version_distance for host '{host}': {e}")
        return float('inf')

@rop_error_handler(error_message="Error finding closest host version")
def find_closest_host_version(node, host_names):
    """
    Finds and sets the closest Houdini host version to the current version if enabled.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node with version parameters.
        host_names (list): List of available host version strings.
    """
    find_closest_version = rops.get_parameter_value(node, "find_closest_version")
    if find_closest_version == 1:
        current_version = hou.applicationVersionString()
        current_version_parts = list(map(int, current_version.split(".")))
        matching_host = min(
            host_names,
            key=lambda host: version_distance(host, current_version_parts)
        )
        rops.set_parameter_value(node, "host_version", matching_host)
        rops.set_parameter_value(node, "find_closest_version", 0)

@rop_error_handler(error_message="Error populating host menu")
def populate_host_menu(node):
    """
    Populates the Houdini version menu for the UI.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node with version parameters.

    Returns:
        list: A list of menu items for the UI, or a default not connected message.
    """
    if not coredata.valid():
        return ["not_connected", "-- Not connected --"]
    software_data = coredata.data()["software"]
    host_names = software_data.supported_host_names()
    find_closest_host_version(node, host_names)
    return [el for host in host_names for el in (host, host.capitalize())]

@rop_error_handler(error_message="Error populating driver menu")
def populate_driver_menu(node):
    """
    Populates the renderer/driver type menu for the UI.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node with driver parameters.

    Returns:
        list: A list of menu items for the UI, or a default not connected message.
    """
    if not coredata.valid():
        return ["not_connected", "-- Not connected --"]
    return [el for i in _get_compatible_plugin_versions(node) for el in (i, i)]

@rop_error_handler(error_message="Error populating extra plugin menu")
def populate_extra_plugin_menu(node):
    """
    Populates the extra plugins menu for the UI.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node with plugin parameters.

    Returns:
        list: A list of menu items for the UI, or a default not connected message.
    """
    if not coredata.valid():
        return ["not_connected", "-- Not connected --"]
    return [el for i in _get_all_plugin_versions(node) for el in (i, i)]

@rop_error_handler(error_message="Error setting plugin")
def set_plugin(node):
    """
    Ensures the driver_version parameter is valid and sets a default if necessary.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node to validate and set the plugin for.
    """
    if not coredata.valid():
        return
    software_data = coredata.data()["software"]
    host_names = software_data.supported_host_names()
    selected_host = node.parm("host_version").eval()
    if selected_host not in host_names:
        selected_host = host_names[-1]
        node.parm("host_version").set(selected_host)
    driver_names = _get_compatible_plugin_versions(node)
    logger.debug(f"set_plugin: driver_names: {driver_names}")
    if not driver_names:
        node.parm('driver_version').set("no_drivers")
        return
    selected_driver = node.parm('driver_version').eval()
    logger.debug(f"set_plugin: selected_driver: {selected_driver}")
    if selected_driver not in driver_names:
        selected_driver = driver_names[-1]
    logger.debug(f"set_plugin: selected_driver: {selected_driver}")
    node.parm('driver_version').set(selected_driver)

@rop_error_handler(error_message="Error ensuring valid software selection")
def ensure_valid_software_selection(node, **kwargs):
    """
    Ensures all software-related parameters (host, driver, extra plugins) are valid.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node to validate selections for.
    """
    if not coredata.valid():
        return
    software_data = coredata.data()["software"]
    host_names = software_data.supported_host_names()
    selected_host = node.parm("host_version").eval()
    if not host_names:
        node.parm("host_version").set("no_houdini_packages")
        node.parm('driver_version').set("no_drivers")
        num_plugins = node.parm("extra_plugins").eval()
        for i in range(1, num_plugins + 1):
            node.parm(f"extra_plugin_{i}").set("no_plugins")
        return
    if selected_host not in host_names:
        selected_host = host_names[-1]
    node.parm("host_version").set(selected_host)
    update_driver_selection(node)
    update_plugin_selections(node)
    driver_names = _get_compatible_plugin_versions(node)
    if not driver_names:
        node.parm('driver_version').set("no_drivers")
        return
    selected_driver = node.parm('driver_version').eval()
    if selected_driver not in driver_names:
        selected_driver = driver_names[-1]
    node.parm('driver_version').set(selected_driver)


@rop_error_handler(error_message="Error ensuring valid software selection")
def ensure_valid_selection(node, **kwargs):
    """
    If connected, ensure the value of this parm is valid.
    """
    if not coredata.valid():
        return

    software_data = coredata.data()["software"]
    host_names = software_data.supported_host_names()
    selected_host = node.parm("host_version").eval()

    if not host_names:
        node.parm("host_version").set("no_houdini_packages")
        node.parm('driver_version').set("no_drivers")
        num_plugins = node.parm("extra_plugins").eval()
        for i in range(1, num_plugins + 1):
            node.parm("extra_plugin_{}".format(i)).set("no_plugins")
        return

    if selected_host not in host_names:
        selected_host = host_names[-1]

    node.parm("host_version").set(selected_host)

    update_driver_selection(node)
    update_plugin_selections(node)

    driver_names = _get_compatible_plugin_versions(node)

    if not driver_names:
        node.parm('driver_version').set("no_drivers")
        return

    selected_driver = node.parm('driver_version').eval()

    if selected_driver not in driver_names:
        selected_driver = driver_names[-1]

    node.parm('driver_version').set(selected_driver)

@rop_error_handler(error_message="Error retrieving compatible plugin versions")
def _get_compatible_plugin_versions(node):
    """
    Retrieves compatible plugin versions for the node's driver.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node to query driver data for.

    Returns:
        list: List of compatible plugin version strings, or error messages if unavailable.
    """
    driver_data = driver.get_driver_data(node)
    if not driver_data:
        return ["No drivers available"]
    conductor_product = driver_data.get("conductor_product", None)
    if not conductor_product:
        return ["No conductor products available"]
    if conductor_product.lower().startswith(("built-in", "unknown")):
        return [driver_data["conductor_product"]]
    if not coredata.valid():
        return []
    software_data = coredata.data().get("software")
    selected_host = node.parm("host_version").eval()
    plugins = software_data.supported_plugins(selected_host)
    plugin_names = [plugin["plugin"] for plugin in plugins]
    if driver_data["conductor_product"] not in plugin_names:
        return [f"No plugins available for {driver_data['conductor_product']}"]
    plugin_versions = []
    for plugin in plugins:
        if plugin["plugin"] == driver_data["conductor_product"]:
            for version in plugin["versions"]:
                plugin_versions.append(f"{plugin['plugin']} {version}")
            break
    return plugin_versions

@rop_error_handler(error_message="Error retrieving all plugin versions")
def _get_all_plugin_versions(node):
    """
    Retrieves all available plugin versions for the selected host.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node with host_version parameter.

    Returns:
        list: List of all plugin version strings, or empty list if unavailable.
    """
    if not coredata.valid():
        return []
    software_data = coredata.data().get("software")
    selected_host = node.parm("host_version").eval()
    plugins = software_data.supported_plugins(selected_host)
    plugin_versions = []
    for plugin in plugins:
        for version in plugin["versions"]:
            plugin_versions.append(f"{plugin['plugin']} {version}")
    return plugin_versions

@rop_error_handler(error_message="Error updating driver selection")
def update_driver_selection(node, **kwargs):
    """
    Updates the driver_version parameter to a valid selection.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node to update.
        **kwargs: Additional keyword arguments (not used in current implementation).
    """
    selected_plugin = node.parm('driver_version').eval()
    plugin_names = _get_compatible_plugin_versions(node)
    if not plugin_names:
        node.parm('driver_version').set("no_plugins_available")
        return
    if selected_plugin not in plugin_names:
        node.parm('driver_version').set(plugin_names[0])

@rop_error_handler(error_message="Error updating plugin selections")
def update_plugin_selections(node, **kwargs):
    """
    Updates extra plugin parameters to valid selections.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node to update.
        **kwargs: Additional keyword arguments (not used in current implementation).
    """
    plugin_names = _get_all_plugin_versions(node)
    extra_plugins = node.parm("extra_plugins")
    if extra_plugins:
        num_plugins = extra_plugins.eval()
        for i in range(1, num_plugins + 1):
            parm = node.parm(f"extra_plugin_{i}")
            selected_plugin = parm.eval()
            if not plugin_names:
                parm.set("no_plugins_available")
                continue
            if selected_plugin not in plugin_names:
                logger.debug(f"setting plugin to: {plugin_names[0]}")
                parm.set(plugin_names[0])
    else:
        logger.debug("No extra plugins parm found.")

@rop_error_handler(error_message="Error resolving software payload")
def resolve_payload(node):
    """
    Resolves the software package IDs for the payload.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node to resolve package IDs for.

    Returns:
        dict: A dictionary with a list of software package IDs.
    """
    ids = set()
    for package in packages_in_use(node):
        ids.add(package["package_id"])
    return {"software_package_ids": list(ids)}

@rop_error_handler(error_message="Error retrieving packages in use")
def packages_in_use(node):
    """
    Retrieves a list of software packages in use based on node parameters.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node with software parameters.

    Returns:
        list: List of package dictionaries, or empty list if unavailable.
    """
    if not coredata.valid():
        return []
    tree_data = coredata.data().get("software")
    if not tree_data:
        return []
    platform = list(coredata.platforms())[0]
    host = node.parm("host_version").eval()
    driver = f"{host}/{node.parm('driver_version').eval()} {platform}"
    paths = [host, driver]
    num_plugins_param = node.parm("extra_plugins")
    if num_plugins_param:
        num_plugins = num_plugins_param.eval()
        for i in range(1, num_plugins + 1):
            parm = node.parm(f"extra_plugin_{i}")
            if parm:
                paths.append(f"{host}/{parm.eval()} {platform}")
    return list(filter(None, [tree_data.find_by_path(path) for path in paths if path]))

@rop_error_handler(error_message="Error adding plugin")
def add_plugin(node, **kwargs):
    """
    Adds a new extra plugin parameter to the UI.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node to add the plugin to.
        **kwargs: Additional keyword arguments (not used in current implementation).
    """
    num_exist = node.parm("extra_plugins").eval()
    node.parm("extra_plugins").set(num_exist + 1)
    update_plugin_selections(node)

@rop_error_handler(error_message="Error removing plugin")
def remove_plugin(node, index):
    """
    Removes an extra plugin parameter at the specified index and shifts subsequent entries.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node to remove the plugin from.
        index (int): The index of the plugin to remove.
    """
    curr_count = node.parm("extra_plugins").eval()
    for i in range(index + 1, curr_count + 1):
        from_parm = node.parm(f"extra_plugin_{i}")
        to_parm = node.parm(f"extra_plugin_{i-1}")
        to_parm.set(from_parm.rawValue())
    node.parm("extra_plugins").set(curr_count - 1)