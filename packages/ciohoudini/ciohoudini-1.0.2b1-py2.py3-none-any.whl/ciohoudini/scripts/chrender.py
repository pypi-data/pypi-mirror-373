#!/usr/bin/env hython
"""
Houdini Conductor Render Script

This script renders a specified Render Operator (ROP) within a Houdini scene using the `hython` interpreter.
It supports various ROP types (e.g., Mantra, Arnold, Redshift, Karma, USD Render) and handles tasks such as
path normalization, driver preparation, and output path resolution. The script is designed to be executed
from the command line with arguments specifying the driver, frame range, and hip file.

Dependencies:
- subprocess: Standard library for running external processes
- sys: Standard library for system-specific parameters
- os: Standard library for OS interactions
- re: Standard library for regular expressions
- argparse: Standard library for command-line argument parsing
- pxr: Pixar USD library for USD stage handling
- logging: Standard library for logging
- string: Standard library for string constants
- hou: Houdini Python module
"""

import subprocess
import sys
import os
import re
import argparse
from pxr import Usd, UsdRender, Sdf
import logging
from string import ascii_uppercase
import hou

# Initialize
logger = logging.getLogger(__name__)

# Define simulation ROP types
SIM_TYPES = ("baketexture", "geometry", "output", "dop")

# Regular expression to match Windows drive letters
DRIVE_LETTER_RX = re.compile(r"^[a-zA-Z]:")

def error(msg):
    """
    Prints an error message to stderr and exits with a non-zero status code.

    Args:
        msg (str): The error message to display.
    """
    if msg:
        sys.stderr.write("\n")
        sys.stderr.write(f"Error: {msg}\n")
        sys.stderr.write("\n")
        sys.exit(1)

def usage(msg=""):
    """
    Prints usage instructions to stderr and exits with an error message.

    Args:
        msg (str, optional): Additional error message to display.
    """
    sys.stderr.write(
        """Usage:

    hython /path/to/chrender.py -d driver -f start end step hipfile
    All flags/args are required

    -d driver:          Path to the output driver that will be rendered
    -f range:           The frame range specification (see below)
    hipfile             The hipfile containing the driver to render
    """
    )
    error(msg)

def prep_ifd(node):
    """
    Prepares a Mantra (IFD) ROP for rendering by setting specific parameters.

    Args:
        node (hou.Node): The Mantra ROP node to prepare.
    """
    logger.info(f"Preparing Mantra ROP node {node.name()}")
    node.parm("vm_verbose").set(3)
    logger.info("Set loglevel to 3")
    node.parm("vm_alfprogress").set(True)
    logger.info("Turn on Alfred style progress")
    node.parm("soho_mkpath").set(True)
    logger.info("Make intermediate directories if needed")

def prep_baketexture(node):
    """
    Prepares a BakeTexture ROP for rendering (currently a no-op).

    Args:
        node (hou.Node): The BakeTexture ROP node to prepare.
    """
    pass

def prep_arnold(node):
    """
    Prepares an Arnold ROP for rendering by setting parameters for robust rendering.

    Args:
        node (hou.Node): The Arnold ROP node to prepare.
    """
    logger.info(f"Preparing Arnold ROP node {node.name()} ...")
    try:
        if node is not None:
            logger.info("Abort on license failure")
            node.parm("ar_abort_on_license_fail").set(True)
            logger.info("Abort on error")
            node.parm("ar_abort_on_error").set(True)
            logger.info("Log verbosity to debug")
            node.parm("ar_log_verbosity").set('debug')
            logger.info("Enable log to console")
            node.parm("ar_log_console_enable").set(True)
    except Exception as e:
        logger.info(f"Error preparing Arnold ROP: {e}")

def prep_redshift(node):
    """
    Prepares a Redshift ROP for rendering by enabling abort conditions and logging.

    Args:
        node (hou.Node): The Redshift ROP node to prepare.
    """
    logger.info(f"Preparing Redshift ROP node {node.name()}")
    logger.info("Turning on abort on license fail")
    node.parm("AbortOnLicenseFail").set(True)
    logger.info("Turning on abort on altus license fail")
    node.parm("AbortOnAltusLicenseFail").set(True)
    logger.info("Turning on abort on Houdini cooking error")
    node.parm("AbortOnHoudiniCookingError").set(True)
    logger.info("Turning on abort on missing resource")
    node.parm("AbortOnMissingResource").set(True)
    logger.info("Turning on Redshift log")
    node.parm("RS_iprMuteLog").set(False)

def prep_karma(node):
    """
    Prepares a Karma ROP for rendering by enabling various debug and output options.

    Args:
        node (hou.Node): The Karma ROP node to prepare.
    """
    logger.info(f"Preparing Karma ROP node {node.name()}")
    logger.info("Turning on Abort for missing texture")
    node.parm("abortmissingtexture").set(True)
    logger.info("Turning on make path")
    node.parm("mkpath").set(True)
    logger.info("Turning on save to directory")
    node.parm("savetodirectory").set(True)
    logger.info("Turning on Husk stdout")
    node.parm("husk_stdout").set(True)
    logger.info("Turning on Husk stderr")
    node.parm("husk_stderr").set(True)
    logger.info("Turning on Husk debug")
    node.parm("husk_debug").set(True)
    logger.info("Turning on log")
    node.parm("log").set(True)
    logger.info("Turning on verbosity")
    node.parm("verbosity").set(True)
    logger.info("Turning on Alfred style progress")
    node.parm("alfprogress").set(True)

def prep_usdrender(node):
    """
    Prepares a USD Render OUT node for rendering by enabling debug and progress options.

    Args:
        node (hou.Node): The USD Render OUT node to prepare.
    """
    logger.info(f"Preparing usdrender OUT node {node.name()}")
    logger.info("Turning on Alfred style progress")
    node.parm("alfprogress").set(True)
    logger.info("Turning on Husk debug")
    node.parm("husk_debug").set(True)
    logger.info("Turning on husk_log")
    node.parm("husk_log").set(True)
    logger.info("Turning on Make Path")
    node.parm("mkpath").set(True)

def prep_usdrender_rop(node):
    """
    Prepares a USD Render ROP for rendering by enabling debug, logging, and path creation.

    Args:
        node (hou.Node): The USD Render ROP node to prepare.
    """
    logger.info(f"Preparing usdrender rop node {node.name()}")
    logger.info("Turning on Alfred style progress")
    node.parm("alfprogress").set(True)
    logger.info("Turning on Husk debug")
    node.parm("husk_debug").set(True)
    logger.info("Turning on husk_log")
    node.parm("husk_log").set(True)
    logger.info("Turning on Make Path")
    node.parm("mkpath").set(True)
    logger.info("Setting verbosity level to 9")
    node.parm("verbose").set(9)

def prep_ris(node):
    """
    Prepares a Renderman ROP (RIS) for rendering by setting log level and directory creation.

    Args:
        node (hou.Node): The Renderman ROP node to prepare.
    """
    logger.info(f"Preparing Ris ROP node {node.name()}")
    node.parm("loglevel").set(4)
    logger.info("Set loglevel to 4")
    node.parm("progress").set(True)
    logger.info("Turn progress on")
    num_displays = node.parm("ri_displays").eval()
    for i in range(num_displays):
        logger.info(f"Set display {i} to make intermediate directories if needed")
        node.parm(f"ri_makedir_{i}").set(True)

def prep_vray_renderer(node):
    """
    Prepares a V-Ray ROP for rendering (currently a no-op due to lack of specific parameters).

    Args:
        node (hou.Node): The V-Ray ROP node to prepare.
    """
    logger.info(f"Preparing V-Ray ROP node {node.name()}")
    logger.info("Nothing to do")

def prep_geometry(node):
    """
    Prepares a Geometry ROP for rendering (currently a no-op).

    Args:
        node (hou.Node): The Geometry ROP node to prepare.
    """
    pass

def prep_output(node):
    """
    Prepares an Output ROP for rendering (currently a no-op).

    Args:
        node (hou.Node): The Output ROP node to prepare.
    """
    pass

def prep_dop(node):
    """
    Prepares a DOP ROP for rendering by enabling time range, path creation, and progress.

    Args:
        node (hou.Node): The DOP ROP node to prepare.
    """
    node.parm("trange").set(1)
    node.parm("mkpath").set(True)
    node.parm("alfprogress").set(True)

def prep_opengl(node):
    """
    Prepares an OpenGL ROP for rendering (currently a no-op).

    Args:
        node (hou.Node): The OpenGL ROP node to prepare.
    """
    pass

def run_driver_prep(rop_node):
    """
    Runs the appropriate preparation function for the given ROP based on its type.

    Args:
        rop_node (hou.Node): The ROP node to prepare.
    """
    rop_type = rop_node.type().name().split(":")[0]
    try:
        fn = globals()[f"prep_{rop_type}"]
        logger.info(f"Running prep function for ROP type: {rop_type}")
        logger.info(f"Function: {fn}")
    except KeyError:
        return
    try:
        fn(rop_node)
    except:
        sys.stderr.write(
            f"Failed to run prep function for ROP type: {rop_type}. Skipping.\n"
        )
        return

def is_sim(rop):
    """
    Checks if the given ROP is a simulation type.

    Args:
        rop (hou.Node): The ROP node to check.

    Returns:
        bool: True if the ROP is a simulation type, False otherwise.
    """
    return rop.type().name().startswith(SIM_TYPES)

def parse_args():
    """
    Parses command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments including driver, frames, and hipfile.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-d", dest="driver", required=True)
    parser.add_argument("-f", dest="frames", nargs=3, type=int)
    parser.add_argument("hipfile", nargs=1)
    args, unknown = parser.parse_known_args()
    if unknown:
        usage(f"Unknown argument(s): {' '.join(unknown)}")
    return args

def ensure_posix_paths():
    """
    Converts Windows-style file paths in Houdini file references to POSIX format.
    """
    refs = hou.fileReferences()
    for parm, value in refs:
        if not parm:
            continue
        try:
            node_name = parm.node().name()
            parm_name = parm.name()
            node_type = parm.node().type().name()
        except:
            logger.info("Failed to get parm info")
            continue
        ident = f"[{node_type}]{node_name}.{parm_name}"
        if node_type.startswith("conductor::job"):
            continue
        printed_not_a_drive_letter = False
        if not DRIVE_LETTER_RX.match(value):
            if not printed_not_a_drive_letter:
                printed_not_a_drive_letter = True
            continue
        logger.info(f"{ident} Found a drive letter in path: {value}. Stripping")
        value = DRIVE_LETTER_RX.sub("", value).replace("\\", "/")
        logger.info(f"{ident} Setting value to {value}")
        try:
            parm.set(value)
        except hou.OperationFailed as ex:
            logger.info(f"{ident} Failed to set value for parm {value}. Skipping")
            logger.info(ex)
            continue
        logger.info(f"{ident} Successfully set value {value}")

def evaluate_custom_output_path(rop):
    """
    Evaluates and prints potential custom output paths for Arnold and USD render nodes.

    Args:
        rop (hou.Node): The ROP node to evaluate.
    """
    try:
        if rop.parm("ar_picture"):
            output_path = rop.parm("ar_picture").eval()
            if output_path:
                logger.info(f"Custom evaluated output path from ar_picture: {output_path}")
        if rop.parm("outputimage"):
            python_expression = rop.parm("outputimage").unexpandedString()
            if "eval" in python_expression:
                try:
                    evaluated_path = eval(python_expression)
                    if evaluated_path:
                        logger.info(f"Custom evaluated output path from Python expression: {evaluated_path}")
                except Exception as eval_error:
                    logger.info(f"Error evaluating Python expression: {str(eval_error)}")
        current_frame = hou.frame()
        if rop.parm("arnold_rendersettings:productName"):
            base_path = rop.parm("arnold_rendersettings:productName").eval()
            dynamic_path = f"{base_path}_frame_{current_frame}"
            logger.info(f"Custom dynamically generated output path: {dynamic_path}")
        if rop.hasParm("custom_output_path"):
            custom_path = rop.parm("custom_output_path").eval()
            if custom_path:
                logger.info(f"Custom output path from custom attribute: {custom_path}")
        if rop.parm("output_template"):
            output_template = rop.parm("output_template").evalAsString()
            if output_template:
                output_path = output_template.replace("$HIPNAME", hou.hipFile.basename())
                output_path = output_path.replace("$OS", rop.name())
                output_path = output_path.replace("$AOV", "beauty")
                logger.info(f"Custom output path from naming pattern: {output_path}")
        if rop.hasParm("scene_override"):
            override_path = rop.parm("scene_override").eval()
            if override_path:
                logger.info(f"Custom output path from scene level override: {override_path}")
        if rop.hasParm("camera_output_path"):
            camera_path = rop.parm("camera_output_path").eval()
            if camera_path:
                logger.info(f"Custom output path based on camera: {camera_path}")
        usd_stage = rop.stage()
        if usd_stage:
            for prim in usd_stage.Traverse():
                if prim.GetTypeName() == "RenderProduct":
                    output_path = prim.GetAttribute("productName").Get()
                    if output_path:
                        logger.info(f"Custom output path from RenderProduct primitive: {output_path}")
        if rop.parm("dependency_output_path"):
            dependency_path = rop.parm("dependency_output_path").eval()
            if dependency_path:
                logger.info(f"Custom output path from linked dependencies: {dependency_path}")
        if rop.parm("aov_output_path"):
            aov_path = rop.parm("aov_output_path").eval()
            if aov_path:
                logger.info(f"Custom output path for AOVs: {aov_path}")
        if rop.parm("frame_output_path"):
            frame_output_path = rop.parm("frame_output_path").eval()
            if frame_output_path:
                logger.info(f"Custom output path for frames: {frame_output_path}")
        if rop.parm("config_output_path"):
            config_output_path = rop.parm("config_output_path").eval()
            if config_output_path:
                logger.info(f"Custom output path from configuration file: {config_output_path}")
        if rop.parm("hda_output_path"):
            hda_output_path = rop.parm("hda_output_path").eval()
            if hda_output_path:
                logger.info(f"Custom output path from HDA: {hda_output_path}")
        if rop.parm("farm_output_path"):
            farm_output_path = rop.parm("farm_output_path").eval()
            if farm_output_path:
                logger.info(f"Custom output path from render farm settings: {farm_output_path}")
        if rop.parm("script_output_path"):
            script_output_path = rop.parm("script_output_path").eval()
            if script_output_path:
                logger.info(f"Custom output path from pre/post-render script: {script_output_path}")
        if rop.parm("user_template_path"):
            user_template_path = rop.parm("user_template_path").eval()
            if user_template_path:
                logger.info(f"Custom output path from user-defined template: {user_template_path}")
        if rop.parm("multipass_output_path"):
            multipass_path = rop.parm("multipass_output_path").eval()
            if multipass_path:
                logger.info(f"Custom output path for multipass rendering: {multipass_path}")
        if rop.parm("node_specific_output"):
            node_specific_path = rop.parm("node_specific_output").eval()
            if node_specific_path:
                logger.info(f"Custom output path from node-specific settings: {node_specific_path}")
    except Exception as e:
        logger.info(f"Error evaluating custom output path: {str(e)}")


def print_output_path(rop):
    """
    Prints the output path for the specified ROP node.

    Args:
        rop (hou.Node): The ROP node to query.
    """
    try:
        output_parm = None
        for parm in [
            "vm_picture", "RS_outputFileNamePrefix", "ar_picture",
            "ri_display_0_name", "SettingsOutput_img_file_path",
            "vm_uvoutputpicture1", "picture", "outputimage",
            "lopoutput", "sopoutput", "dopoutput"
        ]:
            if rop.parm(parm):
                output_parm = rop.parm(parm)
                break
        if output_parm:
            output_path = output_parm.eval()
            logger.info(f"ROP '{rop.name()}' will write to: {output_path}")
        else:
            logger.info(f"ROP '{rop.name()}' does not have a recognized output parameter.")
    except Exception as e:
        logger.info(f"Error occurred while retrieving the output path for ROP '{rop.name()}': {str(e)}")

def render(args):
    """
    Renders the specified ROP within a Houdini scene based on provided arguments.

    Args:
        args: Namespace object with hipfile, driver, and frames attributes.
    """
    hipfile = args.hipfile[0]
    driver = args.driver
    frames = args.frames
    logger.info(f"hipfile: '{hipfile}'")
    logger.info(f"driver: '{driver}'")
    logger.info(f"frames: 'From: {frames[0]} to: {frames[1]}' by: {frames[2]}")
    try:
        hou.hipFile.load(hipfile)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
    rop = hou.node(driver)
    if rop:
        print_output_path(rop)
        render_rop(rop, frames)
    else:
        print_available_rops(driver)

def print_available_rops(driver):
    """
    Prints the list of available ROPs in the current Houdini session to stderr.
    """
    try:
        sys.stderr.write(f"ROP does not exist: '{driver}' \n")
        all_rops = hou.nodeType(hou.sopNodeTypeCategory(), "ropnet").instances()
        sys.stderr.write("Available ROPs:\n")
        for r in all_rops:
            sys.stderr.write(f"  {r.path()}\n")
    except Exception as e:
        sys.stderr.write("Failed to get available ROPs\n")


def render_rop(rop, frames):
    """
    Renders the specified ROP with the given frame range.

    Args:
        rop (hou.Node): The ROP node to render.
        frames (tuple): Start frame, end frame, and frame step.
    """
    try:
        logger.info("Ensure POSIX paths")
        ensure_posix_paths()
        run_driver_prep(rop)
        hou.hipFile.save()
        if rop.type().name() == "topnet":
            rop.displayNode().cookWorkItems(block=True)
        # If the ROP is a simulation type, render without a frame range
        elif is_sim(rop):
            rop.render(verbose=True, output_progress=True)
        # Otherwise, render with the specified frame range
        else:
            rop.render(
                frame_range=tuple(frames),
                verbose=True,
                output_progress=True,
                method=hou.renderMethod.FrameByFrame,
            )
    except hou.OperationFailed as e:
        sys.stderr.write(f"Error rendering the rop: {e}\n")
        return

# Execute the render with parsed arguments
render(parse_args())