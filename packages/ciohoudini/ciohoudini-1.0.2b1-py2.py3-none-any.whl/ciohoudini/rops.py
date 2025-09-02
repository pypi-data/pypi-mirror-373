"""
Houdini Conductor Submitter Script

This script provides functionality for submitting render jobs from Houdini to Conductor,
supporting various render node types and task templates. It includes utilities for
retrieving node types, parameter values, and evaluating Houdini paths and parameters.

Dependencies:
- hou: Houdini Python module
- os: Standard library for OS interactions
- ciohoudini: Custom Houdini utilities for Conductor
- pxr: Pixar USD library
- ciocore.loggeria: Custom logging for Conductor
"""

import hou
import os
from ciopath.gpath import Path
from ciopath.gpath_list import PathList

from ciohoudini import driver, frames, render_rops, software
from ciohoudini.util import rop_error_handler
from pxr import Usd, UsdRender, Sdf

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

# Dictionary defining node types and their properties
nodes_dict = {
    "job": {
        "name": "job",
        "render_rop_paths": True,
        "render_rop_list": True,
        "multi_rop": True,
        "render_delegate": False,
        "image_output_source": False,
        "hython_command": True,
        "task_template_source": False,
    },
    "legacy": {
        "name": "legacy",
        "title": "Conductor Legacy Submitter",
        "render_rop_paths": True,
        "render_rop_list": True,
        "multi_rop": True,
        "render_delegate": False,
        "image_output_source": False,
        "hython_command": True,
        "task_template_source": False,
    },
    "rop": {
        "name": "rop",
        "title": "Conductor Rop Submitter",
        "render_rop_paths": True,
        "render_rop_list": True,
        "multi_rop": False,
        "render_delegate": True,
        "image_output_source": False,
        "import_image_output": True,
        "hython_command": True,
        "task_template_source": False,
    },
    "solaris": {
        "name": "solaris",
        "title": "Conductor Solaris Submitter",
        "render_rop_paths": True,
        "render_rop_list": True,
        "multi_rop": False,
        "render_delegate": True,
        "image_output_source": False,
        "import_image_output": True,
        "hython_command": True,
        "task_template_source": False,
    },
    "husk": {
        "name": "husk",
        "title": "Conductor Husk Submitter",
        "render_rop_paths": True,
        "render_rop_list": True,
        "multi_rop": False,
        "render_delegate": True,
        "image_output_source": False,
        "import_image_output": True,
        "hython_command": False,
        "husk_command": True,
        "usd_filepath": True,
        "task_template_source": False,
    },
    "generator": {
        "name": "generator",
        "title": "Conductor Generator",
        "render_rop_paths": True,
        "render_rop_list": True,
        "multi_rop": False,
        "render_delegate": True,
        "image_output_source": True,
        "chunk_size": True,
        "hython_command": True,
        "generation": True,
        "task_template_source": False,
    },
    "scheduler": {
        "name": "scheduler",
        "title": "Conductor PDG Scheduler",
        "render_rop_paths": True,
        "render_rop_list": False,
        "multi_rop": False,
        "render_delegate": True,
        "image_output_source": True,
        "chunk_size": False,
        "hython_command": False,
        "generation": False,
        "scheduler_command": True,
        "task_template_source": False,
    },
}

"""
Task template dictionary for render job commands.
- {first}: Starting frame of the render.
- {count}: Total number of frames to render.
- {step}: Frame increment (e.g., 1 for every frame, 2 for every second frame).
- {image_output}: Path to the rendered output file(s), typically with frame variables like $F4.
- {render_delegate}: Hydra render delegate (e.g., HdKarma, HdStorm).
- {usd_filepath}: Path to the USD file to render.
"""
task_templates_dict = {
    "hython": "{hserver}hython {render_script} -f {first} {last} {step} -d {render_rop} -o {image_output} {render_scene}", #Hython Command
    "husk": "husk --verbose 9 -f {first} -n {count} -i {step} -o {image_output} --renderer {render_delegate} {usd_filepath}", #Husk
    "scheduler": 'python3 {pdg_script} --hip_file {render_scene} --topnet_path {topnet_path} --item_index {workitem_index} --working_dir {working_dir}',
    "arnold_renderer_kick": "kick -i {usd_filepath} -frames {first}-{last} -step {step} -o {image_output} --renderer {render_delegate}",# Arnold Renderer Kick
    "pixar_usd_record": "usdrecord --verbose 9 --frames {first}:{last}:{step} -o {image_output} --renderer {render_delegate} {usd_filepath}", #Pixar USD Record
    "pixar_renderman": "prman --frames {first}:{last}:{step} -o {image_output} --renderer {render_delegate} {usd_filepath}", #Pixar RenderMan
    "redshift_commandline_renderer": "redshiftCmdLine -l {usd_filepath} -f {first} -e {last} -s {step} -o {image_output} --renderer {render_delegate}", #Redshift Command Line Renderer
    "nvidia_omniverse_kit": "kit-cli-render {usd_filepath} --frames {first}:{last}:{step} -o {image_output} --renderer {render_delegate}", #NVIDIA Omniverse Kit
    "hydra_viewe_usdview": "usdview {usd_filepath} --renderer {render_delegate} --frames {first}:{last}:{step} --output {image_output}", #Hydra Viewer (usdview)
}

@rop_error_handler(error_message="Error determining node type")
def get_node_type(node):
    """
    Determines the node type by checking if its type name contains any key from nodes_dict.

    Args:
        node (hou.Node): The Houdini submitter node

    Returns:
        str: The matching node type key, or None if no match is found and no error occurs.

    Raises:
        hou.NodeError: If an unexpected exception occurs during node type retrieval.
        TypeError: If the provided node is None.
    """
    if not node:
        raise TypeError("Invalid node provided: node cannot be None.")
    node_type_name = node.type().name()
    for key in nodes_dict:
        if key in node_type_name:
            return key
    return None

@rop_error_handler(error_message="Error retrieving node list")
def get_node_list(parm):
    """
    Retrieves a list of node types that support a specific parameter.

    Args:
        parm (str): The parameter to check in nodes_dict.

    Returns:
        list: List of node type keys that support the parameter.

    Raises:
        hou.NodeError: If an unexpected exception occurs during the process.
    """
    node_list = []
    for key in nodes_dict:
        target = nodes_dict[key]
        if parm in target and target.get(parm, False):
            node_list.append(key)
    return node_list

@rop_error_handler(error_message="Error retrieving parameter value")
def get_parameter_value(node, parm_name, string_value=False, unexpand=False):
    """
    Retrieves the value of a parameter on a given Houdini node.

    Args:
        node (hou.Node): The Houdini Conductor Submitter Node containing the parameter.
        parm_name (str): The name of the parameter to retrieve.
        string_value (bool): If True, returns the parameter value as a string.
        unexpand (bool): If True, returns the unexpanded string value of the parameter.

    Returns:
        The parameter value, or None if not found.
    """
    parm = node.parm(parm_name)
    if parm:
        if unexpand:
            return parm.unexpandedString()
        if string_value:
            return parm.evalAsString()
        return parm.eval()
    return None

@rop_error_handler(error_message="Error setting parameter value")
def set_parameter_value(node, parm_name, value):
    """
    Sets the value of a parameter on a given Houdini node.

    Args:
        node (hou.Node): The Houdini Conductor Submitter Node containing the parameter.
        parm_name (str): The name of the parameter to set.
        value: The value to set on the parameter.
    """
    if node:
        parm = node.parm(parm_name)
        if parm:
            parm.set(value)
        else:
            logger.debug(f"Parameter not found: {parm_name}")
    else:
        logger.debug("Node not found.")

@rop_error_handler(error_message="Error retrieving default render script")
def get_default_render_script():
    """
    Retrieves the default render script path based on environment variables.

    Returns:
        str: The default render script path.

    Raises:
        hou.NodeError: If CIODIR environment variable is not set or an unexpected error occurs.
    """
    ciodir = os.environ.get("CIODIR")
    if not ciodir:
        raise RuntimeError("CIODIR environment variable not set. Cannot determine default render script path.")
    render_script = f"{ciodir}/ciohoudini/scripts/chrender.py"
    if not os.path.exists(render_script):
        raise RuntimeError(f"Default render script not found at expected path: {render_script}")
    return render_script

@rop_error_handler(error_message="Error setting default task template")
def set_default_task_template(node, **kwargs):
    """
    Sets the default task template for rendering based on node type.

    Args:
        node (hou.Node): The Houdini Conductor Submitter Node to set the task template for.
        **kwargs: Additional keyword arguments (not used in current implementation).
    """
    node_type = get_node_type(node)
    node_list = get_node_list("task_template_source")
    if node_type in node_list:
        get_default_task_template(node)

@rop_error_handler(error_message="Error retrieving default task template")
def get_default_task_template(node):
    """
    Retrieves the default task template for rendering based on node type.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node

    Returns:
        str: The default task template for render jobs.

    Raises:
        hou.NodeError: If a task template cannot be determined or an unexpected error occurs.
        TypeError: If the provided node is None.
    """
    if not node:
        raise TypeError("Invalid node provided to get_default_task_template: node cannot be None.")
    node_type = get_node_type(node)
    hython_list = get_node_list("hython_command")
    husk_list = get_node_list("husk_command")
    generator_list = get_node_list("task_template_source")
    scheduler_list = get_node_list("scheduler_command")
    task_template = None
    if node_type in hython_list:
        task_template = get_hython_task_template(node)
    elif node_type in husk_list:
        task_template = get_husk_task_template(node)
    elif node_type in generator_list:
        task_template = get_generator_task_template(node)
    elif node_type in scheduler_list:
        task_template = get_scheduler_task_template(node)
    if not task_template:
        raise RuntimeError(f"Could not determine a default task template for node '{node.path()}' of type '{node_type}'.")
    set_parameter_value(node, "task_template", task_template)
    return task_template

@rop_error_handler(error_message="Error retrieving husk task template")
def get_husk_task_template(node: hou.Node) -> str:
    """
    Retrieves the husk task template for rendering.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node.

    Returns:
        str: The husk task template for render jobs.

    Raises:
        hou.NodeError: If the husk task template is not found, the node is invalid,
                       or an unexpected error occurs (handled by rop_error_handler).
    """
    if not isinstance(node, hou.Node):
        raise hou.NodeError(f"Expected hou.Node, got {type(node).__name__}")
    task_template = task_templates_dict["husk"]
    if not task_template:
        raise hou.NodeError(f"Husk task template not found in task_templates_dict for node '{node.path()}'")
    return task_template

@rop_error_handler(error_message="Error retrieving generator task template")
def get_generator_task_template(node):
    """
    Retrieves the task template for generator nodes.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node

    Returns:
        str: The task template for generator render jobs.

    Raises:
        hou.NodeError: If a task template cannot be determined or an unexpected error occurs.
        TypeError: If the provided node is None.
    """
    if not node:
        raise TypeError("Invalid node provided to get_generator_task_template: node cannot be None.")
    task_template_source = get_parameter_value(node, "task_template_source", string_value=True)
    if not task_template_source:
        raise RuntimeError(f"Task template source parameter 'task_template_source' is empty on node '{node.path()}'.")
    task_template = task_templates_dict.get(task_template_source)
    if not task_template:
        raise RuntimeError(f"Task template for source '{task_template_source}' not found in task_templates_dict.")
    return task_template

@rop_error_handler(error_message="Error retrieving scheduler task template")
def get_scheduler_task_template(node: hou.Node) -> str:
    """
    Retrieves the scheduler task template for cooking PDG nodes

    Args:
        node (hou.Node): The Houdini PDG scheduler node

    Returns:
        str: The scheduler task template

    Raises:
        hou.NodeError: If the scheduler task template is not found, the node is invalid,
                       or an unexpected error occurs (handled by rop_error_handler).
    """
    if not isinstance(node, hou.Node):
        raise hou.NodeError(f"Expected hou.Node, got {type(node).__name__}")
    task_template = task_templates_dict["scheduler"]
    if not task_template:
        raise hou.NodeError(f"scheduler task template not found in task_templates_dict for node '{node.path()}'")
    return task_template

@rop_error_handler(error_message="Error retrieving Hython task template")
def get_hython_task_template(node):
    """
    Retrieves the Hython task template for rendering.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node

    Returns:
        str: The Hython task template for render jobs.

    Raises:
        hou.NodeError: If the Hython task template is not found or an unexpected error occurs.
    """
    task_template = task_templates_dict.get("hython")
    if not task_template:
        raise RuntimeError("Hython task template not found in task_templates_dict.")
    return task_template

@rop_error_handler(error_message="Error checking root path")
def is_root_path(current_path):
    """
    Checks if the given path resolves to a root directory using ciopath.

    A root directory is one whose parent directory is itself after normalization.
    This handles cases for POSIX, Windows, and UNC paths.

    Args:
        current_path (str or Path): The path to check, either as a string or ciopath Path object.

    Returns:
        bool: True if the path is a root directory, False otherwise.

    Examples:
        POSIX:
            is_root_path("/") == True
            is_root_path("/my_render") == False
            is_root_path("/foo/bar") == False
        Windows:
            is_root_path("C:\\") == True
            is_root_path("C:/") == True
            is_root_path("C:\\my_render") == False
            is_root_path("\\\\server\\share") == True (UNC path root)
            is_root_path("\\\\server\\share\\folder") == False
    """
    if not current_path:
        return False
    path_obj = current_path if isinstance(current_path, Path) else Path(current_path)
    normalized_path = path_obj.fslash(with_drive=True)
    if path_obj.absolute:
        if not path_obj.components:
            return True
        parent_components = path_obj.components[:-1]
        parent_path = Path(parent_components, context={}) if parent_components else Path("/")
        if path_obj.drive_letter:
            parent_path = Path([path_obj.drive_letter] + parent_components, context={})
        return normalized_path == parent_path.fslash(with_drive=True)
    return False

@rop_error_handler(error_message="Error determining Solaris image output")
def get_solaris_image_output(driver_path):
    """
    Determines the proper output path for rendered images for a Houdini submission to Conductor.

    The output_path is the directory containing the rendered images, set in the output_path field
    of the job payload. It does not influence where the DCC/render will be output. The function
    follows these steps:
    1. Check the Override Output Image on the USDRender ROP. If set, use its directory.
    2. Get the path for the Render Settings primitive from the USDRender ROP.
    3. Get the stage from the input node of the USDRender ROP.
    4. Using the USD API, find the primitive for the Render Settings path.
    5. Using the USD API, find all Render Product prims linked via the 'products' relationship.
    6. Get the productName from each Render Product primitive (paths to be rendered, including filename).
       The parent folder of the productName is used to set the output_path.
    7. If multiple Render Product primitives are found, proceed to Step 8.
    8. For multiple Render Products, get the lowest level common path. Ensure it is not a root path
       and has a consistent root.

    Args:
        driver_path (str): The path to the USD Render ROP node.

    Returns:
        str: The determined output directory path (using forward slashes),
             or an empty string if resolution fails or encounters an error.
    """
    output_directory = ""
    logger.debug(f"Attempting to determine the proper output path for rendered images for driver: {driver_path}")

    try:
        driver_node = hou.node(driver_path)
        if not driver_node:
            logger.debug(f"Could not find USD Render ROP node at path: {driver_path}")
            return ""

        # Step 1: Check the Override Output Image on the USDRender ROP
        output_image_parm = driver_node.parm("outputimage")
        if output_image_parm:
            raw_output_path = output_image_parm.unexpandedString()
            expanded_output_path = hou.expandStringAtFrame(raw_output_path, hou.frame())
            if expanded_output_path and expanded_output_path.strip():
                output_path_obj = Path(expanded_output_path)
                # Use the full path as per the original code (not dirname)
                output_directory = output_path_obj.fslash(with_drive=True)
                logger.debug(
                    f"Step 1: Override Output Image is set on the USDRender ROP. Using directory: '{output_directory}'")
                logger.debug(
                    "Validation 1: Code to check the USDRender ROP for an image path should be visually verified in the Houdini UI.")
                return output_directory

        logger.debug("Step 1: Override Output Image on the USDRender ROP is not set or empty, proceed to Step 2.")


        # Step 2: Get the path for the Render Settings primitive from the USDRender ROP
        rendersettings_parm = driver_node.parm("rendersettings")
        if not rendersettings_parm:
            logger.debug(f"Node {driver_path} missing 'rendersettings' parameter.")
            return ""
        rendersettings_path = Sdf.Path(rendersettings_parm.evalAsString())
        if not rendersettings_path:
            logger.debug(f"'rendersettings' parameter on {driver_path} is empty.")
            return ""
        logger.debug(f"Step 2: Get the path for the Render Settings primitive from the USDRender ROP: {rendersettings_path}")

        # Step 3: Get the stage from the input node of the USDRender ROP
        inputs = driver_node.inputs()
        if not inputs:
            logger.debug(f"Failure state 1: Check that the USDRender ROP {driver_path} has an input node.")
            return ""
        input_node = inputs[0]
        stage = None
        stage_source_node_path = ""
        if hasattr(input_node, "stage") and input_node.stage():
            stage = input_node.stage()
            stage_source_node_path = input_node.path()
        else:
            # Search ancestors for a stage
            queue = list(input_node.inputs())
            visited = {input_node}
            visited.update(queue)
            while queue:
                current_node = queue.pop(0)
                if hasattr(current_node, "stage") and current_node.stage():
                    stage = current_node.stage()
                    stage_source_node_path = current_node.path()
                    break
                for inp in current_node.inputs():
                    if inp and inp not in visited:
                        visited.add(inp)
                        queue.append(inp)
        if not stage:
            logger.debug(f"Failure state 2: Check that the input node {input_node.path()} to the USDRender ROP has a stage.")
            return ""
        logger.debug(f"Step 3: Successfully obtained the stage from the input node: {stage_source_node_path}")

        # Step 4: Using the USD API, find the primitive that corresponds to the path of the Render Settings
        rendersettings_prim = stage.GetPrimAtPath(rendersettings_path)
        if not rendersettings_prim or not rendersettings_prim.IsValid():
            logger.debug(f"Step 4: Could not find the primitive that corresponds to the path of the Render Settings at: {rendersettings_path}")
            return ""
        logger.debug(f"Step 4: Using the USD API, found the primitive that corresponds to the path of the Render Settings: {rendersettings_prim.GetPath()}")

        # Step 5: Using the USD API, find all Render Product prims linked via the 'products' relationship
        product_paths = []
        products_rel = rendersettings_prim.GetRelationship("products")
        if products_rel and products_rel.HasAuthoredTargets():
            product_prim_paths = products_rel.GetTargets()
            logger.debug(f"Step 5: Using the USD API, found {len(product_prim_paths)} Render Product prims linked via the 'products' relationship: {product_prim_paths}")

            # Step 6: Get the productName from each Render Product primitive
            for product_path in product_prim_paths:
                product_prim = stage.GetPrimAtPath(product_path)
                if product_prim and product_prim.GetTypeName() == "RenderProduct":
                    product_name_attr = product_prim.GetAttribute("productName")
                    if product_name_attr and product_name_attr.HasAuthoredValue():
                        product_name = product_name_attr.Get()
                        if product_name and str(product_name).strip():
                            product_paths.append(str(product_name))
                            logger.debug(f"Step 6: Get the productName '{product_name}' from Render Product primitive: {product_prim.GetPath()}")
                        else:
                            logger.warning(f"Render Product primitive {product_prim.GetPath()} has empty 'productName' attribute.")
                    else:
                        logger.warning(f"Render Product primitive {product_prim.GetPath()} is missing 'productName' attribute or it has no authored value.")
                else:
                    logger.warning(f"Prim at {product_path} is not a valid Render Product or does not exist.")
        else:
            logger.debug("Step 5: No 'products' relationship found on Render Settings primitive, checking descendants as fallback.")
            # Fallback: Check descendants
            for prim in Usd.PrimRange(rendersettings_prim):
                if prim == rendersettings_prim:
                    continue
                if prim.GetTypeName() == "RenderProduct":
                    product_name_attr = prim.GetAttribute("productName")
                    if product_name_attr and product_name_attr.HasAuthoredValue():
                        product_name = product_name_attr.Get()
                        if product_name and str(product_name).strip():
                            product_paths.append(str(product_name))
                            logger.debug(f"Step 6: Get the productName '{product_name}' from Render Product primitive: {prim.GetPath()} (via descendant traversal)")
                        else:
                            logger.warning(f"Render Product primitive {prim.GetPath()} has empty 'productName' attribute (via descendant traversal).")
                    else:
                        logger.warning(f"Render Product primitive {prim.GetPath()} is missing 'productName' attribute or it has no authored value (via descendant traversal).")

        # Failure State 3: If there are no products under render settings
        if not product_paths:
            logger.debug(f"Failure state 3: If there are no products under render settings then issue a validation error for Render Settings primitive: {rendersettings_path}")
            logger.debug("Validation 4: Presence or absence of render products under the render settings primitive should be visually verified in the Houdini UI (Stage Geometry Spreadsheet).")
            return ""

        logger.debug(f"Step 6-2: Found {len(product_paths)} productName(s): {product_paths}")
        # Validation 5: Prompt user to verify product names in Houdini UI
        logger.debug("Validation 5: Existence of product name(s) should be visually verified in the Houdini UI.")

        # Step 7: Check for multiple Render Product primitives
        if len(product_paths) == 1:
            output_directory = os.path.dirname(product_paths[0])
            logger.debug(f"Step 7: Single Render Product primitive found. Using parent folder of productName: '{output_directory}'")
        else:
            logger.debug(f"Step 7: Multiple Render Product primitives ({len(product_paths)}) found, go to Step 8.")
            # Step 8: For multiple Render Products, get the lowest level common path
            normalized_paths = [os.path.normpath(p) for p in product_paths]
            try:
                common_path = os.path.commonpath(normalized_paths)
                if not common_path or not common_path.strip():
                    logger.debug(f"Failure state 4: If there are multiple render products as children of render settings that do not have a common path, then issue a validation error. Products: {product_paths}")
                    # Validation 6 & 7: Prompt user to verify
                    logger.debug("Validation 6: Presence or absence of render products under the render settings primitive should be visually verified in the Houdini UI.")
                    logger.debug("Validation 7: Existence of product name(s) should be visually verified in the Houdini UI.")
                    return ""
                if is_root_path(common_path):
                    logger.debug(f"Failure state 4: If there are multiple render products as children of render settings that do not have a common path, then issue a validation error. Common path '{common_path}' resolves to a root path. Products: {product_paths}")
                    logger.debug("Validation 6: Presence or absence of render products under the render settings primitive should be visually verified in the Houdini UI.")
                    logger.debug("Validation 7: Existence of product name(s) should be visually verified in the Houdini UI.")
                    return ""
                output_directory = common_path
                logger.debug(f"Step 8: For multiple Render Products, get the lowest level common path: '{output_directory}'")
            except ValueError as e:
                logger.debug(f"Failure state 4: If there are multiple render products as children of render settings that do not have a common path, then issue a validation error. Error: {e}. Products: {product_paths}")
                logger.debug("Validation 6: Presence or absence of render products under the render settings primitive should be visually verified in the Houdini UI.")
                logger.debug("Validation 7: Existence of product name(s) should be visually verified in the Houdini UI.")
                return ""

        # Final step: Ensure consistent forward slashes
        final_path = output_directory.replace("\\", "/")
        logger.debug(f"Final determined proper output path for rendered images: '{final_path}'")
        return final_path

    except hou.OperationFailed as e:
        logger.debug(f"Houdini operation failed while processing {driver_path}: {e}")
        return ""
    except Exception as e:
        logger.debug(f"Unexpected error determining the proper output path for rendered images for {driver_path}: {e}")
        return ""

@rop_error_handler(error_message="Error checking override output path", warning_only=True)
def get_override_output_path(driver_node):
    """
    Checks the 'outputimage' parameter on the USDRender ROP and returns its directory.

    Args:
        driver_node (hou.Node): The USD Render ROP node.

    Returns:
        str: The directory of the override output image path.

    Raises:
        hou.NodeError: If the driver node is invalid, the 'outputimage' parameter is not set or invalid,
                      or an unexpected error occurs.
    """

    if not driver_node:
        logger.debug("No driver node provided for checking override output path.")
        return None
    output_image_parm = driver_node.parm("outputimage")
    if not output_image_parm:
        logger.debug(f"Node {driver_node.path()} missing 'outputimage' parameter.")
    raw_output_path = output_image_parm.unexpandedString()
    expanded_output_path = hou.expandStringAtFrame(raw_output_path, hou.frame())
    if not expanded_output_path or not expanded_output_path.strip():
        logger.debug(f"'outputimage' parameter on {driver_node.path()} is empty or evaluates to an empty string.")
    output_path_obj = Path(expanded_output_path)
    if not output_path_obj.components:
        logger.debug(f"Evaluated output path '{expanded_output_path}' for node {driver_node.path()} is a root path or invalid.")
    output_directory_obj = Path(output_path_obj.components[:-1], context={})
    if output_path_obj.drive_letter and not output_directory_obj.components:
        output_directory_obj = Path([output_path_obj.drive_letter], context={})
    output_directory = output_directory_obj.fslash(with_drive=True)
    if not output_directory or "INVALID FILENAME" in output_directory or "UNKNOWN INPUT" in output_directory:
        logger.debug(f"Could not determine a valid output directory from path '{expanded_output_path}' for node {driver_node.path()}.")
    logger.debug(f"Step 1: Override Output Image is set on the USDRender ROP. Using directory: '{output_directory}'")
    logger.debug("Validation 1: Code to check the USDRender ROP for an image path should be visually verified in the Houdini UI.")
    return output_directory

@rop_error_handler(error_message="Error retrieving render settings path")
def get_render_settings_path(driver_node):
    """
    Retrieves the 'rendersettings' parameter from the USDRender ROP.

    Args:
        driver_node (hou.Node): The USD Render ROP node.

    Returns:
        Sdf.Path: The path to the Render Settings primitive, or None if not found.
    """
    if not driver_node:
        raise hou.NodeError("No driver node provided for retrieving render settings path.")
    rendersettings_parm = driver_node.parm("rendersettings")
    if not rendersettings_parm:
        raise hou.NodeError(f"Node {driver_node.path()} missing 'rendersettings' parameter.")
    rendersettings_path = Sdf.Path(rendersettings_parm.evalAsString())
    if not rendersettings_path:
        raise hou.NodeError(f"'rendersettings' parameter on {driver_node.path()} is empty.")
    logger.debug(f"Step 2: Get the path for the Render Settings primitive from the USDRender ROP: {rendersettings_path}")
    return rendersettings_path

@rop_error_handler(error_message="Error finding USD stage")
def find_usd_stage(driver_node):
    """
    Finds the USD stage from the input node of the USDRender ROP or its ancestors.

    Args:
        driver_node (hou.Node): The USD Render ROP node.

    Returns:
        tuple: (stage, stage_source_node_path), or (None, "") if not found.
    """
    if not driver_node:
        raise hou.NodeError("No driver node provided for finding USD stage.")
    inputs = driver_node.inputs()
    if not inputs:
        raise hou.NodeError(f"Failure state 1: Check that the USDRender ROP {driver_node.path()} has an input node.")
    input_node = inputs[0]
    stage = None
    stage_source_node_path = ""
    if hasattr(input_node, "stage") and input_node.stage():
        stage = input_node.stage()
        stage_source_node_path = input_node.path()
    else:
        queue = list(input_node.inputs())
        visited = {input_node}
        visited.update(queue)
        while queue:
            current_node = queue.pop(0)
            if hasattr(current_node, "stage") and current_node.stage():
                stage = current_node.stage()
                stage_source_node_path = current_node.path()
                break
            for inp in current_node.inputs():
                if inp and inp not in visited:
                    visited.add(inp)
                    queue.append(inp)
        if not stage:
            raise hou.NodeError(f"Failure state 2: Check that the input node {input_node.path()} to the USDRender ROP has a stage.")
    logger.debug(f"Step 3: Successfully obtained the stage from the input node: {stage_source_node_path}")
    return stage, stage_source_node_path

@rop_error_handler(error_message="Error retrieving render settings primitive")
def get_render_settings_prim(stage, rendersettings_path):
    """
    Finds the Render Settings primitive using the USD API.

    Args:
        stage (Usd.Stage): The USD stage.
        rendersettings_path (Sdf.Path): The path to the Render Settings primitive.

    Returns:
        Usd.Prim: The Render Settings primitive, or None if not found.
    """
    if not stage or not rendersettings_path:
        raise hou.NodeError("Invalid stage or rendersettings path provided.")
    rendersettings_prim = stage.GetPrimAtPath(rendersettings_path)
    if not rendersettings_prim or not rendersettings_prim.IsValid():
        raise hou.NodeError(f"Step 4: Could not find the primitive that corresponds to the path of the Render Settings at: {rendersettings_path}")
    logger.debug(f"Step 4: Using the USD API, found the primitive that corresponds to the path of the Render Settings: {rendersettings_prim.GetPath()}")
    return rendersettings_prim

@rop_error_handler(error_message="Error retrieving render product paths")
def get_render_product_paths(rendersettings_prim):
    """
    Finds all Render Product primitives and extracts their productName attributes.

    Args:
        rendersettings_prim (Usd.Prim): The Render Settings primitive.

    Returns:
        list: List of productName paths (as strings), or empty list if none found.
    """
    product_paths = []
    if not rendersettings_prim:
        raise hou.NodeError("No Render Settings primitive provided for finding Render Product paths.")
    products_rel = rendersettings_prim.GetRelationship("products")
    if products_rel and products_rel.HasAuthoredTargets():
        product_prim_paths = products_rel.GetTargets()
        logger.debug(f"Step 5: Using the USD API, found {len(product_prim_paths)} Render Product prims linked via the 'products' relationship: {product_prim_paths}")
        for product_path in product_prim_paths:
            product_prim = rendersettings_prim.GetStage().GetPrimAtPath(product_path)
            if product_prim and product_prim.GetTypeName() == "RenderProduct":
                product_name_attr = product_prim.GetAttribute("productName")
                if product_name_attr and product_name_attr.HasAuthoredValue():
                    product_name = product_name_attr.Get()
                    if product_name and str(product_name).strip():
                        product_paths.append(str(product_name))
                        logger.debug(f"Step 6: Get the productName '{product_name}' from Render Product primitive: {product_prim.GetPath()}")
                    else:
                        logger.warning(f"Render Product primitive {product_prim.GetPath()} has empty 'productName' attribute.")
                else:
                    logger.warning(f"Render Product primitive {product_path} is missing 'productName' attribute or it has no authored value.")
            else:
                logger.warning(f"Prim at {product_path} is not a valid Render Product or does not exist.")
    else:
        logger.debug("Step 5: No 'products' relationship found on Render Settings primitive, checking descendants as fallback.")
        for prim in Usd.PrimRange(rendersettings_prim):
            if prim == rendersettings_prim:
                continue
            if prim.GetTypeName() == "RenderProduct":
                product_name_attr = prim.GetAttribute("productName")
                if product_name_attr and product_name_attr.HasAuthoredValue():
                    product_name = product_name_attr.Get()
                    if product_name and str(product_name).strip():
                        product_paths.append(str(product_name))
                        logger.debug(f"Step 6: Get the productName '{product_name}' from Render Product primitive: {prim.GetPath()} (via descendant traversal)")
                    else:
                        logger.warning(f"Render Product primitive {prim.GetPath()} has empty 'productName' attribute (via descendant traversal).")
                else:
                    logger.warning(f"Render Product primitive {prim.GetPath()} is missing 'productName' attribute or it has no authored value (via descendant traversal).")
    if not product_paths:
        logger.debug("Validation 4: Presence or absence of render products under the render settings primitive should be visually verified in the Houdini UI (Stage Geometry Spreadsheet).")
        logger.debug("Validation 5: Existence of product name(s) should be visually verified in the Houdini UI.")
    return product_paths

@rop_error_handler(error_message="Error computing output directory")
def compute_output_directory(product_paths):
    """
    Computes the output directory from one or more product paths.

    Args:
        product_paths (list): List of productName paths (as strings).

    Returns:
        str: The computed output directory path, or empty string if invalid.
    """
    if not product_paths:
        return ""
    if len(product_paths) == 1:
        output_path_obj = Path(product_paths[0])
        output_directory = Path(output_path_obj.components[:-1], context={}).fslash(with_drive=True) if output_path_obj.components else ""
        logger.debug(f"Step 7: Single Render Product primitive found. Using parent folder of productName: '{output_directory}'")
        return output_directory
    path_list = PathList(*product_paths)
    common_path_obj = path_list.common_path()
    if not common_path_obj or not common_path_obj.fslash().strip():
        logger.debug("Validation 6: Presence or absence of render products under the render settings primitive should be visually verified in the Houdini UI.")
        logger.debug("Validation 7: Existence of product name(s) should be visually verified in the Houdini UI.")
        return ""
    if is_root_path(common_path_obj):
        logger.debug("Validation 6: Presence or absence of render products under the render settings primitive should be visually verified in the Houdini UI.")
        logger.debug("Validation 7: Existence of product name(s) should be visually verified in the Houdini UI.")
        return ""
    output_directory = common_path_obj.fslash(with_drive=True)
    logger.debug(f"Step 8: For multiple Render Products, get the lowest level common path: '{output_directory}'")
    return output_directory

@rop_error_handler(error_message="Error determining Solaris image output")
def get_solaris_image_output_fragments(driver_path):
    """
    Determines the proper output path for rendered images for a Houdini submission to Conductor.

    The output_path is the directory containing the rendered images, set in the output_path field
    of the job payload. It does not influence where the DCC/render will be output. The function
    follows these steps:
    1. Check the Override Output Image on the USDRender ROP. If set, use its directory.
    2. Get the path for the Render Settings primitive from the USDRender ROP.
    3. Get the stage from the input node of the USDRender ROP.
    4. Using the USD API, find the primitive for the Render Settings path.
    5. Using the USD API, find all Render Product prims linked via the 'products' relationship.
    6. Get the productName from each Render Product primitive (paths to be rendered, including filename).
       The parent folder of the productName is used to set the output_path.
    7. If multiple Render Product primitives are found, proceed to Step 8.
    8. For multiple Render Products, get the lowest level common path. Ensure it is not a root path
       and has a consistent root.

    Args:
        driver_path (str): The path to the USD Render ROP node.

    Returns:
        str: The determined output directory path (using forward slashes),
             or an empty string if resolution fails.
    """
    logger.debug(f"Attempting to determine the proper output path for rendered images for driver: {driver_path}")
    driver_node = hou.node(driver_path)
    if not driver_node:
        logger.debug("No driver node provided for checking override output path.")
        return None
    output_directory = get_override_output_path(driver_node)
    if output_directory:
        return output_directory
    rendersettings_path = get_render_settings_path(driver_node)
    if not rendersettings_path:
        return ""
    stage, stage_source_node_path = find_usd_stage(driver_node)
    if not stage:
        return ""
    rendersettings_prim = get_render_settings_prim(stage, rendersettings_path)
    if not rendersettings_prim:
        return ""
    product_paths = get_render_product_paths(rendersettings_prim)
    if not product_paths:
        return ""
    return compute_output_directory(product_paths)

@rop_error_handler(error_message="Error finding USD stage node")
def find_usd_stage_node(driver_node):
    """
    Checks the immediate upstream node for a valid USD stage.

    Args:
        driver_node (hou.Node): The Houdini Conductor Submitter Node to start the search from.

    Returns:
        hou.Node: The parent node with a valid USD stage, or None if not found.
    """
    inputs = driver_node.inputs()
    if inputs:
        parent_node = inputs[0]
        if hasattr(parent_node, "stage"):
            return parent_node
    return None

@rop_error_handler(error_message="Error retrieving render delegate")
def get_render_delegate(node):
    """
    Retrieves the render delegate for the render ROP node and sets it on the node.

    Args:
        node (hou.Node): The Houdini Conductor Submitter Node to retrieve the render delegate for.

    Returns:
        str: The render delegate, defaults to "BRAY_HdKarma" if not found.
    """
    render_delegate = None
    node_type = get_node_type(node)
    if node_type not in ["husk"]:
        driver_path = get_parameter_value(node, "driver_path")
        if driver_path:
            render_rop_node = hou.node(driver_path)
            if render_rop_node:
                render_delegate = get_parameter_value(render_rop_node, "renderer", string_value=True)
                if render_delegate:
                    set_parameter_value(node, "render_delegate", render_delegate)
    else:
        render_delegate = get_parameter_value(node, "render_delegate", string_value=True)
        if render_delegate and "karma" in render_delegate.lower():
            render_delegate = "BRAY_HdKarma"
    return render_delegate

@rop_error_handler(error_message="Error setting USD path")
def set_usd_path(node, **kwargs):
    """
    Sets the USD file path for the render ROP node if it exists.
    This function reloads the USD path, updating the Preview accordingly.

    Args:
        node (hou.Node): The Houdini Conductor Submitter Node to set the USD file path for.
        **kwargs: Additional keyword arguments (not used in current implementation).
    """
    usd_path = get_parameter_value(node, "usd_filepath")
    if usd_path:
        set_parameter_value(node, "usd_filepath", usd_path)

@rop_error_handler(error_message="Error setting render software")
def set_render_software(node, **kwargs):
    """
    Sets the render software for the render ROP node, ensuring a valid selection.

    Args:
        node (hou.Node): The Houdini Conductor Submitter Node to set the render software for.
        **kwargs: Additional keyword arguments (not used in current implementation).
    """
    logger.debug("Setting render software")
    software.ensure_valid_selection(node)

@rop_error_handler(error_message="Error querying output folder", warning_only=True)
def query_output_folder_path(node, rop_path=None):
    """
    Queries the output folder path for a given node, resolving Houdini parameters.

    Args:
        node (hou.Node): The Houdini Conductor Submitter node
        rop_path (str, optional): The specific ROP path to look up.

    Returns:
        str: The output folder path as a forward-slash normalized string, or empty string if not available.
    """
    image_path = get_parameter_value(node, "override_image_output", string_value=True)
    if image_path:
        image_path_obj = Path(image_path)
        output_folder_obj = Path(image_path_obj.components[:-1], context={}) if image_path_obj.components else Path(".")
        if output_folder_obj.relative:
            hip_path = Path(os.path.expandvars("$HIP"))
            output_folder_obj = Path(os.path.join(hip_path.fslash(), output_folder_obj.fslash()))
        return output_folder_obj.fslash(with_drive=True)
    return ""

@rop_error_handler(error_message="Error querying output folder", warning_only=True)
def query_output_folder_path_2(node, rop_path=None):
    """
    Queries the output folder path for a given node, resolving Houdini parameters.

    Args:
        node (hou.Node): The Houdini node to query.
        rop_path (str, optional): The specific ROP path to look up.

    Returns:
        str: The output folder path as a forward-slash normalized string, or empty string if not available.
    """
    output_folder = ""
    image_path = get_parameter_value(node, "override_image_output", string_value=True)
    if image_path and image_path.strip():
            # Create a Path object for platform-independent handling
            image_path_obj = Path(image_path)
            if image_path_obj.components:
                # Extract parent directory by removing the last component
                output_folder_obj = Path(image_path_obj.components[:-1], context={})
                output_folder = output_folder_obj.fslash(with_drive=True)
            else:
                logger.debug(f"Image path '{image_path}' has no components, returning empty folder.")

    return output_folder

@rop_error_handler(error_message="Error querying output folder", warning_only=True)
def query_output_folder(node, rop_path=None):
    """
    Queries the output folder path for a given node, resolving Houdini parameters.

    Args:
        node (hou.Node): The Houdini node to query.
        rop_path (str, optional): The specific ROP path to look up.

    Returns:
        str: The output folder path, or empty string if not available.
    """
    output_folder = ""
    image_path = get_parameter_value(node, "override_image_output", string_value=True)
    if image_path:
        # Convert Houdini-style path to OS-compatible path
        image_path = os.path.normpath(image_path)
        # Extract the directory portion
        output_folder = os.path.dirname(image_path)
        # Ensure consistent forward slashes
        output_folder = output_folder.replace("\\", "/")

    return output_folder

@rop_error_handler(error_message="Error copying parameters")
def copy_parameters(src_node, dest_node):
    """
    Copies parameter values from the source node to the destination node, skipping specified parameters.

    Args:
        src_node (hou.Node): The source node to copy parameters from.
        dest_node (hou.Node): The destination node to copy parameters to.
    """
    skip_params = {'asset_regex', 'asset_excludes'}
    for parm in src_node.parms():
        parm_name = parm.name()
        if parm_name in skip_params:
            continue
        dest_parm = dest_node.parm(parm_name)
        if dest_parm:
            dest_parm.set(parm.eval())

@rop_error_handler(error_message="Error generating Solaris nodes")
def generate_solaris_nodes(node, **kwargs):
    """
    Creates a subnet connected to the current node and adds conductor nodes for each ROP path.

    Args:
        node (hou.Node): The Houdini Conductor Submitter Node to which the subnet will be connected.
        **kwargs: Additional keyword arguments for future extensions.
    """
    existing_subnet_count = 0
    for output_node in node.outputs():
        if output_node.type().name() == "subnet":
            existing_subnet_count += 1
    subnet_rank = existing_subnet_count + 1
    subnet_name = f"solaris_subnet_{subnet_rank}"
    parent = node.parent()
    subnet = parent.createNode("subnet", subnet_name)
    subnet.moveToGoodPosition()
    for child in subnet.children():
        if "input" in child.name():
            child.destroy()
    render_rops_data = render_rops.get_render_rop_data(node)
    if not render_rops_data:
        logger.debug("No render ROP data found.")
        return None
    previous_node = None
    for index, render_rop in enumerate(render_rops_data):
        rop_path = render_rop.get("path", None)
        if not rop_path:
            continue
        base_node_name = f"conductor_{rop_path.split('/')[-1]}"
        node_name = f"{base_node_name}_{subnet_rank}"
        solaris_node = subnet.createNode("conductor::conductor_solaris_submitter::0.1", node_name, run_init_scripts=False)
        solaris_node.moveToGoodPosition()
        copy_parameters(node, solaris_node)
        solaris_node.parm("driver_path").set(rop_path)
        if previous_node:
            solaris_node.setInput(0, previous_node)
        solaris_node.parm("driver_path").set(rop_path)
        previous_node = solaris_node
    subnet.layoutChildren()
    subnet.setInput(0, node)
    logger.debug(f"Successfully created the subnet '{subnet_name}' and connected the nodes.")