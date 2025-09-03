"""
Houdini Conductor Validation Module

This module provides validation logic for Conductor submissions in Houdini. It defines
a set of validator classes to check various aspects of the submission configuration,
such as image output paths, USD file paths, driver paths, and more. The validators
identify errors, warnings, and notices to ensure a robust submission process.

Dependencies:
- os: Standard library for OS interactions
- sys: Standard library for system-specific parameters
- re: Standard library for regular expressions
- hou: Houdini Python module
- logging: Standard library for logging
- ciocore: Core Conductor utilities (validator, loggeria)
- ciohoudini: Custom Houdini utilities (rops)
"""

import os
import re
from ciocore.validator import Validator
from ciocore import data as coredata
import hou

from ciohoudini import rops


try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

class ValidateImageOutputLegalPath(Validator):
    """
    Validates that the override_image_output path is not too shallow (e.g., root drives or top-level directories).
    """
    def run(self, _):
        """
        Checks if the image output path is a shallow root directory and adds an error if so.

        Args:
            _: Unused argument (required by Validator interface).
        """
        node = self._submitter
        image_output_param = node.parm("override_image_output")

        # Skip if parameter doesn't exist or is empty
        if not image_output_param:
            return
        image_output_path = image_output_param.eval().strip()
        if not image_output_path:
            return

        # Resolve Houdini variables (e.g., $HIP, $JOB)
        try:
            resolved_path = hou.expandString(image_output_path)
        except Exception:
            resolved_path = image_output_path

        # Normalize path: lowercase, forward slashes, no trailing slashes
        normalized = resolved_path.replace("\\", "/").rstrip("/").lower()

        # Check for shallow Windows drive (e.g., 'C:' or 'D:/')
        shallow_drive = re.match(r"^[a-z]:/?$", normalized)

        # Check for shallow Unix/Mac paths
        shallow_unix_paths = ["/users", "/home", "/user"]
        is_shallow_unix = normalized in shallow_unix_paths

        # Add error if path is too shallow
        if shallow_drive or is_shallow_unix:
            msg = (
                f"The resolved image output path '{resolved_path}' is too shallow.\n"
                "Please use a deeper folder structure in Render Products (e.g., '/Users/yourname/project/render') "
                "to avoid organizational or permission issues during rendering."
            )
            self.add_error(msg)

class ValidateUpstreamStage(Validator):
    """
    Validates that the immediate upstream node of a Solaris driver has a valid USD stage.
    """
    def run(self, _):
        """
        Checks for a valid USD stage in the upstream node of a Solaris driver.

        Args:
            _: Unused argument (required by Validator interface).
        """
        try:
            node = self._submitter
            node_type = rops.get_node_type(node)

            if node_type in ["solaris"]:
                driver_path_param = node.parm("driver_path")

                # Check if driver_path parameter exists
                if not driver_path_param:
                    self.add_error("The 'driver_path' parameter is missing on the node.")
                    return

                driver_path = driver_path_param.eval().strip()
                """
                # Check if driver_path is set
                if not driver_path:
                    self.add_error("The 'driver_path' parameter is empty. Please specify a valid driver path.")
                    return
                """

                driver_node = hou.node(driver_path)

                # Check if driver node exists
                if not driver_node:
                    self.add_error(f"Driver node not found at path: {driver_path}")
                    return

                image_output_path = ""
                image_output_param = node.parm("override_image_output")

                if image_output_param:
                    image_output_path = image_output_param.eval().strip()

                if not image_output_path:
                    # Check for valid USD stage in upstream node
                    if not rops.find_usd_stage_node(driver_node):
                        msg = "No valid USD stage found in the immediate upstream node. Please ensure the driver node is connected to a valid stage."
                        self.add_error(msg)
        except Exception as e:
            logger.error(f"Error validating upstream stage: {e}")

class ValidateDriverPath(Validator):
    """
    Validates that the driver_path parameter is set for Solaris or ROP nodes.
    """
    def run(self, _):
        """
        Ensures the driver_path parameter is set for Solaris or ROP nodes.

        Args:
            _: Unused argument (required by Validator interface).
        """
        node = self._submitter
        node_type = rops.get_node_type(node)

        if node_type in ["solaris", "rop"]:
            driver_path_param = node.parm("driver_path")

            # Check if driver_path is set and not empty
            if not driver_path_param or not driver_path_param.eval().strip():
                msg = (
                    "The 'driver_path' parameter is not set. "
                    "Please select a valid driver before submission."
                )
                self.add_error(msg)

class ValidateImageOutputPath(Validator):
    """
    Validates the override_image_output parameter, ensuring the folder exists or can be created.
    """
    def run(self, _):
        """
        Checks if the image output folder exists, attempting to create it if it doesn't.

        Args:
            _: Unused argument (required by Validator interface).
        """
        node = self._submitter
        image_output_param = node.parm("override_image_output")

        # Skip if parameter doesn't exist
        if not image_output_param:
            return

        image_output_path = image_output_param.eval().strip()

        # Check if image output path is set
        if not image_output_path:
            node_type = rops.get_node_type(node)
            if node_type not in ["solaris"]:
                msg = (
                    "The 'override_image_output' parameter is not set. "
                    "Please specify a valid file path for image output before submission."
                )
                self.add_error(msg)
                return

        # Resolve Houdini variables
        try:
            resolved_path = hou.expandString(image_output_path)
        except Exception as e:
            resolved_path = image_output_path
            logger.debug(f"Failed to resolve path: {e}")

        # Get folder path
        folder_path = os.path.dirname(resolved_path)

        # Check and create folder if necessary
        if folder_path:
            if not os.path.exists(folder_path):
                try:
                    os.makedirs(folder_path)
                    msg = (
                        f"The folder '{folder_path}' did not exist and was created successfully."
                    )
                    self.add_warning(msg)
                except Exception as e:
                    msg = (
                        f"The folder '{folder_path}' did not exist and could not be created. "
                        f"Error: {e}"
                    )
                    self.add_error(msg)

class ValidateUSDFilePath(Validator):
    """
    Validates the usd_filepath parameter, ensuring it is set and exists on disk.
    """
    def run(self, _):
        """
        Checks if the USD file path is set and exists on disk.

        Args:
            _: Unused argument (required by Validator interface).
        """
        node = self._submitter
        usd_filepath_param = node.parm("usd_filepath")

        # Skip if parameter doesn't exist
        if not usd_filepath_param:
            return

        usd_filepath = usd_filepath_param.eval().strip()

        # Check if USD file path is set
        if not usd_filepath:
            msg = (
                "The 'usd_filepath' parameter is not set. "
                "Please specify a valid USD file path before submission."
            )
            self.add_error(msg)
            return

        # Resolve Houdini variables
        try:
            resolved_filepath = hou.expandString(usd_filepath)
        except Exception as e:
            resolved_filepath = usd_filepath
            logger.debug(f"Failed to resolve path: {e}")

        # Check if file exists
        if not os.path.exists(resolved_filepath):
            msg = (
                f"The specified USD file path '{usd_filepath}' resolves to '{resolved_filepath}', "
                "but it does not exist on disk. Please verify the path and ensure the file is accessible "
                "before submission."
            )
            self.add_error(msg)

class ValidateUploadDaemon(Validator):
    """
    Validates the uploader daemon configuration for submissions using a daemon.
    """
    def run(self, _):
        """
        Adds notices and warnings for daemon-based submissions.

        Args:
            _: Unused argument (required by Validator interface).
        """
        node = self._submitter
        use_daemon = node.parm("use_daemon").eval()
        if not use_daemon:
            return

        location = node.parm("location_tag").eval().strip()
        if location:
            msg = (
                f"This submission expects an uploader daemon to be running and set to a specific location tag. "
                f"Please make sure that you have installed ciocore from the Conductor Companion app "
                f"and that you have started the daemon with the --location flag set to the same location tag."
                f"After you press submit you can open a shell and type: conductor uploader --location \"{location}\""
            )
        else:
            msg = (
                "This submission expects an uploader daemon to be running.\n"
                "Please make sure that you have installed ciocore from the Conductor Companion app "
                "After you press submit you can open a shell and type: \"conductor uploader\""
            )
        self.add_notice(msg)

        # Add warning about asset accessibility
        self.add_warning(
            "Since you are using an uploader daemon, you'll want to make sure that all your assets are "
            "accessible by the machine on which the daemon is running.\n You can check the list of upload assets in the Preview tab.\n"
            "Just hit the Do Asset Scan button and scroll down to the bottom."
        )

class ValidateScoutFrames(Validator):
    """
    Validates scout frame configurations to warn about potentially costly setups.
    """
    def run(self, _):
        """
        Adds warnings for scout frame configurations that may lead to unexpected costs.

        Args:
            _: Unused argument (required by Validator interface).
        """
        node = self._submitter
        use_scout_frames = node.parm("use_scout_frames").eval()
        scout_count = node.parm("scout_frame_task_countx").eval()
        chunk_size = node.parm("chunk_size").eval()
        instance_type_name = node.parm("instance_type").eval()

        # Warn about missing scout frames with best-fit instance types
        if scout_count == 0 and instance_type_name in ["best-fit-cpu", "best-fit-gpu"]:
            msg = (
                "We strongly recommend using Scout Frames with best fit instance types,"
                " as Conductor is not responsible for insufficient render nodes when using Best"
                " Fit instance types."
            )
            self.add_warning(msg)

        # Warn about chunking with scout frames
        if chunk_size > 1 and use_scout_frames:
            msg = (
                "You have chunking set higher than 1."
                " This can cause more scout frames to be rendered than you might expect."
            )
            self.add_warning(msg)

class ValidateResolvedChunkSize(Validator):
    """
    Validates the resolved chunk size to warn about large task counts.
    """
    def run(self, _):
        """
        Adds a warning if the resolved chunk size exceeds the user-specified chunk size.

        Args:
            _: Unused argument (required by Validator interface).
        """
        try:
            node = self._submitter
            chunk_size = node.parm("chunk_size").eval()
            resolved_chunk_size = node.parm("resolved_chunk_size").eval()

            if chunk_size and resolved_chunk_size:
                chunk_size = int(chunk_size)
                resolved_chunk_size = int(resolved_chunk_size)

                if resolved_chunk_size > chunk_size:
                    msg = (
                        "In one or more render rops, the number of frames per task has been automatically increased to maintain "
                        "a total task count below 800. If you have a time-sensitive deadline and require each frame to be "
                        "processed on a dedicated instance, you might want to consider dividing the frame range into smaller "
                        "portions. "
                        "Alternatively, feel free to reach out to Conductor Customer Support for assistance."
                    )
                    self.add_warning(msg)
        except Exception as e:
            logger.debug(f"ValidateResolvedChunkSize: {e}")

class ValidateGPURendering(Validator):
    """
    Validates rendering settings to warn about CPU rendering with Redshift.
    """
    def run(self, _):
        """
        Adds a warning if Redshift is used with CPU rendering.

        Args:
            _: Unused argument (required by Validator interface).
        """
        node = self._submitter
        instance_type_family = node.parm("instance_type_family").eval().lower()
        driver_software = node.parm("driver_version").eval().lower()

        if "redshift" in driver_software and instance_type_family == "cpu":
            msg = (
                "CPU rendering is selected."
                " We strongly recommend selecting GPU rendering when using the Redshift plugin for Houdini."
            )
            self.add_warning(msg)

class ValidateUploadedFilesWithinOutputFolder(Validator):
    """
    Validates that assets in the output folder are not already uploaded.
    """
    def run(self, _):
        """
        Adds a warning if assets in the output folder are already uploaded and resets the output_excludes parameter.

        Args:
            _: Unused argument (required by Validator interface).
        """
        node = self._submitter
        output_excludes = node.parm("output_excludes").eval()
        output_folder = node.parm("output_folder").eval()

        if output_excludes and output_excludes == 1:
            msg = (
                f"One or more assets in the output folder: {output_folder} "
                "have been identified as already uploaded. "
                "To ensure smooth processing on the render farm and avoid potential conflicts, "
                "these files have been excluded from the list of assets to be uploaded."
                "For successful job submission, please relocate these files to "
                "a different folder and then resubmit your job."
            )
            self.add_warning(msg)
        node.parm("output_excludes").set(0)

class ValidatePaths(Validator):
    """
    Validates file paths in loadlayer USD nodes to warn about using $HOME.
    """
    def run(self, _):
        """
        Adds a warning if $HOME is used in loadlayer node file paths.

        Args:
            _: Unused argument (required by Validator interface).
        """
        stage_node_list = hou.node('/stage').allSubChildren()
        disallowed_list = ["$HOME"]
        for stage_node in stage_node_list:
            if stage_node and stage_node.type().name() == 'loadlayer':
                filepath_param = stage_node.parm("filepath")
                if filepath_param:
                    filepath_value = filepath_param.rawValue()
                    for item_sr in disallowed_list:
                        if item_sr in filepath_value:
                            msg = (
                                "We strongly recommend using an explicit path over using '$HOME' in the filepath of any loadlayer node within the stage as '$HOME' might not be correctly evaluated on the renderfarm."
                            )
                            self.add_warning(msg)


class ValidateConductorConnection(Validator):
    """
    Validates that the submitter node is successfully connected to Conductor.
    Checks coredata status, the 'is_connected' parameter, and scans other
    relevant parameters for 'Not Connected' status strings.
    """
    def run(self, _):
        """
        Checks coredata.valid(), the 'is_connected' parameter, and other
        parameter values of the submitter node to determine connection status.

        Args:
            _: Unused argument (required by Validator interface).
        """
        node = self._submitter
        is_connected_parm = node.parm("is_connected")

        # Primary check: coredata.valid()
        # This reflects the most current state of the connection to the backend.
        is_core_connected = coredata.valid()

        is_parm_indicating_connected = False
        if is_connected_parm is None:
            # This case should ideally not happen if the HDA is correctly defined.
            msg = (
                f"The submitter node '{node.name()}' is missing the 'is_connected' parameter. "
                "This indicates an issue with the HDA definition."
            )
            self.add_error(msg)
            # If the 'is_connected' parm is missing, we rely solely on coredata.valid()
            # and the string check for the error message logic below.
        else:
            is_parm_indicating_connected = bool(is_connected_parm.evalAsInt())

        found_not_connected_in_parm_value = False
        # Parameters like 'project', 'instance_type', 'host_version', 'driver_version'
        # are typically menus or strings that might display "-- Not Connected --"
        # This check helps catch UI inconsistencies or stale data.
        for parm in node.parms():
            parm_template = parm.parmTemplate()
            # Check String and Menu type parameters
            if parm_template.type() in (hou.parmTemplateType.String, hou.parmTemplateType.Menu):
                try:
                    # Use evalAsString() as it works for both String and Menu types
                    # to get the currently displayed value.
                    parm_value = parm.evalAsString()
                    if "not connected" in parm_value.lower(): # Case-insensitive check
                        found_not_connected_in_parm_value = True
                        break  # Found one, no need to check further
                except hou.Error as e:
                    # Log potential issues evaluating a parameter, but don't stop validation
                    logger.debug(
                        f"ValidateConductorConnection: Could not evaluate parameter '{parm.name()}' "
                        f"for 'Not Connected' string: {e}"
                    )

        # Determine if an error should be raised
        # Error if:
        # 1. Core is not connected OR
        # 2. The 'is_connected' parameter is off (even if core might be connected, indicates UI/state mismatch) OR
        # 3. A parameter string explicitly says "Not Connected" (UI mismatch)
        if not is_core_connected or \
           (is_connected_parm is not None and not is_parm_indicating_connected) or \
           found_not_connected_in_parm_value:
            msg = (
                f"The submitter node '{node.name()}' does not appear to be fully connected to Conductor. "
                "This may be indicated by the backend connection status, the 'Connect' status toggle, "
                "or by parameters displaying '-- Not Connected --' (or similar). "
                "Please press the 'Connect' button on the 'Setup' tab to refresh the connection "
                "and parameter values before submitting."
            )
            self.add_error(msg)

def run(*nodes):
    """
    Runs all validators on the provided nodes and collects errors, warnings, and notices.

    Args:
        *nodes: Variable number of Houdini nodes to validate.

    Returns:
        tuple: Lists of errors, warnings, and notices from all validators.
    """
    errors, warnings, notices = [], [], []
    for node in nodes:
        er, wn, nt = _run_validators(node)
        errors.extend(er)
        warnings.extend(wn)
        notices.extend(nt)
    return errors, warnings, notices

def _run_validators(node):
    """
    Executes all registered validators for a single node.

    Args:
        node (hou.Node): The Houdini node to validate.

    Returns:
        tuple: Lists of unique errors, warnings, and notices from all validators.
    """
    takename = node.name()
    validators = [plugin(node) for plugin in Validator.plugins()]
    for validator in validators:
        validator.run(takename)

    # Collect unique errors, warnings, and notices
    errors = list(set.union(*[validator.errors for validator in validators]))
    warnings = list(set.union(*[validator.warnings for validator in validators]))
    notices = list(set.union(*[validator.notices for validator in validators]))
    return errors, warnings, notices