"""
Module for managing assets in the Conductor plugin for Houdini.
"""

import hou
import pxr.UsdUtils
import re
import os
from ciopath.gpath_list import PathList, GLOBBABLE_REGEX
from ciopath.gpath import Path
from ciohoudini import common, rops
from ciohoudini.util import rop_error_handler

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

ADDITIONAL_PATH_PARMS = {
    # === LOPs (Solaris/USD) ===
    'Lop/reference::2.0': ('filepath1',),
    'Lop/usdrender_rop': ('lopoutput',),
    'Lop/layer': ('filepath',),
    'Lop/sublayer': ('filepath',),
    'Lop/payload': ('filepath',),
    'Lop/materiallibrary': ('filepath',),
    'Lop/file': ('filepath',),

    # === SOPs (Geometry / FX / Volumes) ===
    'Sop/file': ('file',),
    'Sop/alembic': ('fileName',),
    'Sop/vm_geo_alembic': ('attribfile',),
    'Sop/attribfrommap': ('file',),
    'Sop/volume': ('file',),
    'Sop/mdd': ('file',),
    'Sop/heightfield_file': ('file',),
    'Sop/pointcloudiso': ('file',),
    'Sop/bgeo': ('file',),
    'Sop/hfile': ('file',),
    'Sop/image': ('filename',),
    'Sop/trace': ('input',),
    'Sop/lineart': ('image',),
    'Sop/pic': ('filename',),

    # === SHOPs / MATs / VOPs (Shading & Lighting) ===
    'Shop/arnold_image': ('filename',),
    'Vop/arnold::image': ('filename',),
    'Shop/arnold_light': ('filename',),
    'Light/arnold_light': ('filename',),
    'Vop/texture': ('map',),
    'Vop/v_texture': ('map',),
    'Light/envlight': ('env_map',),
    'Vop/materialx/mtlximage': ('file',),
    'Vop/arnold::procedural': ('filename',),
    'Vop/arnold::volume': ('filename',),
    'Shop/pxrtexture': ('filename',),
    'Vop/pxrTexture': ('filename',),

    # === Redshift ===
    'Vop/redshift::TextureSampler': ('tex0', 'tex1', 'tex2', 'tex3'),
    'Light/redshift_lightDome': ('tex0',),
    'Light/redshift_IES': ('profile',),
    'Object/redshift_proxy': ('fileName',),
    'Sop/redshift_volume': ('fileName',),

    # === Karma ===
    'Light/karmadomelight::1.0': ('texture',),

    # === ROPs / Drivers ===
    'Driver/geometry': ('sopoutput',),
    'Driver/alembic': ('filename',),
    'Driver/filmboxfbx': ('output',),
    'Driver/mantra': ('vm_picture', 'vm_deepresolver_file'),
    'Driver/usd': ('usdoutput',),
    'Driver/karma': ('picture',),
    'Driver/Redshift_ROP': ('RS_outputFileNamePrefix',),
    'Driver/ifd': ('vm_picture',),
    'Driver/rop_vdbsequence': ('vdb_file_path',),

    # === COPs (Compositing) ===
    'Cop/file': ('filename',),
    'Cop/rop_file_output': ('copoutput',),
    'Cop/composite': ('inputfile',),
    'Cop/generate_thumbnail': ('thumbnail_path',),

    # === CHOPs (Channel / Audio) ===
    'Chop/file': ('file',),
    'Chop/sound': ('file',),
    'Chop/record': ('filename',),
}

@rop_error_handler(error_message="Error resolving payload upload paths")
def resolve_payload(node, **kwargs):
    """
    Resolve the upload_paths field for the payload.
    """
    path_list = PathList()
    path_list.add(*auxiliary_paths(node))
    path_list.add(*extra_paths(node))
    path_list.add(*add_usd_file(node))
    do_asset_scan = kwargs.get("do_asset_scan", False)
    if do_asset_scan:
        path_list.add(*scan_paths(node))

    if not path_list:
        return

    output_folder = ""
    expanded_path = expand_env_vars(node.parm('output_folder').eval())
    if expanded_path:
        output_folder = Path(expanded_path)

    current_assets = []
    seen = set()

    for path in path_list:
        path = str(path).replace("\\", "/")
        normalized = path.lower()
        if normalized not in seen:
            current_assets.append(path)
            seen.add(normalized)

    filtered_paths = [path for path in current_assets if not is_within_output_folder(path, output_folder)]

    if len(current_assets) > len(filtered_paths):
        node.parm("output_excludes").set(0)

    return {"upload_paths": filtered_paths}

@rop_error_handler(error_message="Error checking if path is within output folder")
def is_within_output_folder(path, output_folder):
    """
    Check if a path is within the output folder.
    """
    normalized_path = os.path.normpath(str(path))
    normalized_output_folder = os.path.normpath(str(output_folder))
    return normalized_path.startswith(normalized_output_folder)

@rop_error_handler(error_message="Error collecting auxiliary paths")
def auxiliary_paths(node, **kwargs):
    """
    Add the hip file, the OCIO file, and the render script to the list of assets.
    """
    path_list = PathList()
    path_list.add(hou.hipFile.path())
    ocio_file = os.environ.get("OCIO")
    if ocio_file:
        path_list.add(os.path.dirname(ocio_file))
    render_script = node.parm("render_script").eval()
    if render_script:
        render_script = "{}[{}]".format(render_script[:-1], render_script[-1])
        path_list.add(render_script)
    if path_list:
        path_list = _resolve_absolute_existing_paths(path_list)
    exclude_pattern = node.parm("asset_excludes").unexpandedString()
    if exclude_pattern:
        path_list.remove_pattern(exclude_pattern)
    return path_list

@rop_error_handler(error_message="Error while adding USD file")
def add_usd_file(node):
    """
    Add the USD file to the list of assets.
    """

    path_list = PathList()
    node_type = rops.get_node_type(node)
    node_list = rops.get_node_list("usd_filepath")
    if node_type in node_list:
        usd_file = rops.get_parameter_value(node, "usd_filepath", string_value=True)
        if usd_file:
            path_list.add(usd_file)
            if path_list:
                path_list = _resolve_absolute_existing_paths(path_list)

    return path_list

@rop_error_handler(error_message="Error collecting extra paths")
def extra_paths(node, **kwargs):
    """
    Collect extra paths from the node's extra assets list.
    """
    path_list = PathList()
    num = node.parm("extra_assets_list").eval()
    for i in range(1, num + 1):
        asset = node.parm("extra_asset_{:d}".format(i)).eval()
        asset = os.path.expandvars(asset)
        if asset:
            path_list.add(asset)
    if path_list:
        path_list = _resolve_absolute_existing_paths(path_list)
    return path_list

@rop_error_handler(error_message="Error reading scan configuration")
def read_scan_config(submitter_node):
    """
    Read configuration parameters for asset scanning.
    """
    regex_pattern = submitter_node.parm("asset_regex").unexpandedString()
    exclude_pattern = submitter_node.parm("asset_excludes").unexpandedString()
    REGEX = None
    if regex_pattern:
        REGEX = re.compile(regex_pattern, re.IGNORECASE)
    SEQUENCE_MARKER_REGEX = re.compile(r"\.\d+")
    sequence_like_token_regex = re.compile(r"<udim>|<u>|<v>|<u2>|<v2>|<obj_name>", re.IGNORECASE)
    return regex_pattern, exclude_pattern, REGEX, SEQUENCE_MARKER_REGEX, sequence_like_token_regex

@rop_error_handler(error_message="Error gathering parameters to scan")
def gather_parms_to_scan():
    """
    Gather parameters to scan for file references.
    """
    parms_to_scan = []
    parms_from_refs = _get_file_ref_parms()
    parms_to_scan.extend(parms_from_refs)
    parms_from_additional = _get_additional_file_ref_parms()
    parms_to_scan.extend(parms_from_additional)
    return parms_to_scan

@rop_error_handler(error_message="Error evaluating and expanding paths")
def evaluate_and_expand_paths(parms_to_scan):
    """
    Evaluate parameters and expand variables to collect raw paths.
    """
    raw_paths = PathList()
    processed_parms = set()
    raw_paths_temp = set()
    for parm in parms_to_scan:
        if parm is None or parm in processed_parms:
            continue
        processed_parms.add(parm)
        evaluated = parm.eval()
        if evaluated and isinstance(evaluated, str):
            expanded_str = hou.expandString(evaluated)
            if expanded_str:
                raw_paths_temp.add(expanded_str)
            else:
                raw_paths_temp.add(evaluated)
    for path_str in raw_paths_temp:
        raw_paths.add(path_str)
    return raw_paths

@rop_error_handler(error_message="Error scanning USD dependencies")
def scan_usd_dependencies(raw_paths):
    """
    Scan USD files for dependencies.
    """
    usd_dependencies = set()
    if pxr and pxr.UsdUtils:
        for file_path_obj in list(raw_paths):
            file_path = str(file_path_obj)
            is_usd = False
            if file_path and ('/' in file_path or '\\' in file_path):
                if os.path.isfile(file_path) and os.path.splitext(file_path)[-1].lower() in (".usd", ".usda", ".usdc", ".usdz"):
                    is_usd = True
            if is_usd:
                layers, assets, unresolved = pxr.UsdUtils.ComputeAllDependencies(file_path)
                for layer in layers:
                    if layer.realPath:
                        usd_dependencies.add(layer.realPath)
                usd_dependencies.update(set(assets))
        for dep_path in usd_dependencies:
            raw_paths.add(dep_path)
    return raw_paths

@rop_error_handler(error_message="Error filtering checked paths")
def filter_checked_paths(raw_paths):
    """
    Filter paths using check_path function.
    """
    checked_paths = PathList()
    for path_obj in raw_paths:
        path_str = str(path_obj)
        if check_path(path_str):
            checked_paths.add(path_obj)
    return checked_paths

@rop_error_handler(error_message="Error categorizing paths for resolution")
def categorize_paths_for_resolution(checked_paths, REGEX, SEQUENCE_MARKER_REGEX, sequence_like_token_regex):
    """
    Apply regex substitution and categorize paths for globbing or specific checks.
    """
    paths_for_globbing = PathList()
    paths_for_specific_check = PathList()
    if REGEX:
        for path_obj in checked_paths:
            path_str = str(path_obj)
            pth_sub_wildcarded = REGEX.sub(r"*", path_str)
            is_explicit_sequence = False
            if SEQUENCE_MARKER_REGEX.search(path_str) and pth_sub_wildcarded != path_str:
                is_explicit_sequence = True
            elif sequence_like_token_regex.search(path_str) and pth_sub_wildcarded != path_str:
                is_explicit_sequence = True
            if is_explicit_sequence:
                paths_for_globbing.add(pth_sub_wildcarded)
            else:
                paths_for_specific_check.add(path_str)
    else:
        paths_for_specific_check = checked_paths
    return paths_for_globbing, paths_for_specific_check

@rop_error_handler(error_message="Error resolving final paths")
def resolve_final_paths(paths_for_globbing, paths_for_specific_check):
    """
    Resolve paths with or without globbing.
    """
    final_resolved_paths = PathList()
    if paths_for_globbing:
        resolved_globbed_paths = _resolve_absolute_existing_paths(paths_for_globbing, perform_glob=True)
        final_resolved_paths.add(*list(resolved_globbed_paths))
    if paths_for_specific_check:
        resolved_specific_paths = _resolve_absolute_existing_paths(paths_for_specific_check, perform_glob=False)
        final_resolved_paths.add(*list(resolved_specific_paths))
    return final_resolved_paths

@rop_error_handler(error_message="Error applying exclude pattern")
def apply_exclude_pattern(final_resolved_paths, exclude_pattern):
    """
    Apply exclude pattern to filter out paths.
    """
    if exclude_pattern:
        final_resolved_paths.remove_pattern(exclude_pattern)
    return final_resolved_paths

@rop_error_handler(error_message="Error scanning paths for assets")
def scan_paths(submitter_node):
    """
    Scans the Houdini scene for assets referenced by various nodes, configured by the submitter node.
    """
    logger.debug("=" * 20 + " Starting Asset Scan " + "=" * 20)
    logger.debug(f"Submitter Node: {submitter_node.path()}")

    regex_pattern, exclude_pattern, REGEX, SEQUENCE_MARKER_REGEX, sequence_like_token_regex = read_scan_config(submitter_node)
    parms_to_scan = gather_parms_to_scan()
    raw_paths = evaluate_and_expand_paths(parms_to_scan)
    raw_paths = scan_usd_dependencies(raw_paths)
    checked_paths = filter_checked_paths(raw_paths)
    paths_for_globbing, paths_for_specific_check = categorize_paths_for_resolution(checked_paths, REGEX, SEQUENCE_MARKER_REGEX, sequence_like_token_regex)
    final_resolved_paths = resolve_final_paths(paths_for_globbing, paths_for_specific_check)
    final_resolved_paths = apply_exclude_pattern(final_resolved_paths, exclude_pattern)

    logger.debug("=" * 20 + " Asset Scan Finished " + "=" * 20)
    logger.debug(f">>> Found {len(final_resolved_paths)} final asset paths.")
    return final_resolved_paths

@rop_error_handler(error_message="Error retrieving file reference parameters")
def _get_file_ref_parms():
    """
    Retrieve file reference parameters from the Houdini scene.
    """
    parms = []
    refs = hou.fileReferences()
    for parm, ref_path in refs:
        if parm:
            node_type_name = parm.node().type().nameWithCategory()
            if not node_type_name.startswith("conductor::"):
                parms.append(parm)
    return parms

@rop_error_handler(error_message="Error retrieving additional file reference parameters")
def _get_additional_file_ref_parms():
    """
    Retrieve additional file reference parameters based on node types.
    """
    parms = []
    all_categories = hou.nodeTypeCategories()
    for node_type_key, node_parms_tuple in ADDITIONAL_PATH_PARMS.items():
        category_name_str = None
        type_name_with_version = None
        if '/' in node_type_key:
            parts = node_type_key.split('/', 1)
            category_name_str = parts[0]
            type_name_with_version = parts[1]
        else:
            continue
        type_name_base = type_name_with_version.split('::')[0]
        category_obj = all_categories.get(category_name_str)
        if not category_obj:
            continue
        node_type_obj = hou.nodeType(category_obj, type_name_base)
        if node_type_obj is None:
            continue
        instances = node_type_obj.instances()
        if not instances:
            continue
        for node_instance in instances:
            for parm_name in node_parms_tuple:
                additional_parm = node_instance.parm(parm_name)
                if additional_parm:
                    parms.append(additional_parm)
    return parms

@rop_error_handler(error_message="Error clearing all assets")
def clear_all_assets(node, **kwargs):
    """
    Clear all extra assets from the node.
    """
    node.parm("extra_assets_list").set(0)

@rop_error_handler(error_message="Error browsing for files")
def browse_files(node, **kwargs):
    """
    Browse for files to add to the assets list.
    """
    files = hou.ui.selectFile(
        title="Browse for files to upload",
        collapse_sequences=True,
        file_type=hou.fileType.Any,
        multiple_select=True,
        chooser_mode=hou.fileChooserMode.Read,
    )
    if not files:
        return
    files = [f.strip() for f in files.split(";") if f.strip()]
    add_entries(node, *files)

@rop_error_handler(error_message="Error browsing for folder")
def browse_folder(node, **kwargs):
    """
    Browse for a folder to add to the assets list.
    """
    files = hou.ui.selectFile(title="Browse for folder to upload", file_type=hou.fileType.Directory)
    if not files:
        return
    files = [f.strip() for f in files.split(";") if f.strip()]
    add_entries(node, *files)

@rop_error_handler(error_message="Error adding asset entries")
def add_entries(node, *entries):
    """
    Add asset entries to the node's extra assets list.
    """
    path_list = PathList()
    num = node.parm("extra_assets_list").eval()
    for i in range(1, num + 1):
        asset = node.parm("extra_asset_{:d}".format(i)).eval()
        asset = os.path.expandvars(asset)
        if asset:
            path_list.add(asset)
    for entry in entries:
        path_list.add(entry)
    paths = [p.fslash() for p in path_list]
    node.parm("extra_assets_list").set(len(paths))
    for i, arg in enumerate(paths):
        index = i + 1
        node.parm("extra_asset_{:d}".format(index)).set(arg)

@rop_error_handler(error_message="Error removing asset")
def remove_asset(node, index):
    """
    Remove an asset from the extra assets list by index.
    """
    curr_count = node.parm("extra_assets_list").eval()
    for i in range(index + 1, curr_count + 1):
        from_parm = node.parm("extra_asset_{}".format(i))
        to_parm = node.parm("extra_asset_{}".format(i - 1))
        to_parm.set(from_parm.unexpandedString())
    node.parm("extra_assets_list").set(curr_count - 1)

@rop_error_handler(error_message="Error adding HDA paths")
def add_hdas(node, **kwargs):
    """
    Add HDA paths to the assets list.
    """
    hda_paths = [hda.libraryFilePath() for hda in common.get_plugin_definitions()]
    if not hda_paths:
        return
    add_entries(node, *hda_paths)

@rop_error_handler(error_message="Error resolving absolute existing paths")
def _resolve_absolute_existing_paths(path_list_input, perform_glob=True):
    """
    Resolve absolute paths and optionally perform globbing.
    """
    logger.debug(f"    >>> _resolve_absolute_existing_paths called with {len(path_list_input)} items. Perform Glob: {perform_glob}")
    hip = hou.getenv("HIP")
    job = hou.getenv("JOB")
    internals = ("op:", "temp:")
    resolved = PathList()
    for path_obj_or_str in path_list_input:
        if isinstance(path_obj_or_str, str):
            current_path = Path(path_obj_or_str)
        else:
            current_path = path_obj_or_str
        if current_path.relative:
            if not str(current_path).startswith(internals):
                if hip:
                    resolved.add(os.path.join(hip, str(current_path)))
                if job:
                    resolved.add(os.path.join(job, str(current_path)))
        else:
            resolved.add(current_path)
    resolved.remove_missing()
    if perform_glob:
        resolved.glob()
    logger.debug(f"    <<< _resolve_absolute_existing_paths returning {len(resolved)} items.")
    return resolved

@rop_error_handler(error_message="Error expanding environment variables")
def expand_env_vars(path):
    """
    Expand environment variables in a path.
    """
    return os.path.expandvars(path)

@rop_error_handler(error_message="Error checking path validity")
def check_path(file_path):
    """
    Check if a file path is valid for inclusion.
    """
    if not file_path:
        return False
    file_path = file_path.replace("\\", "/")
    if "*" in file_path:
        return False
    if file_path.startswith("/tmp/"):
        return False
    if "houdini_temp" in file_path:
        return False
    hip_folder = hou.getenv("HIP")
    if hip_folder:
        normalized_file_path = os.path.normpath(os.path.abspath(file_path))
        normalized_hip_folder = os.path.normpath(os.path.abspath(hip_folder))
        if normalized_file_path == normalized_hip_folder:
            return False
    return True