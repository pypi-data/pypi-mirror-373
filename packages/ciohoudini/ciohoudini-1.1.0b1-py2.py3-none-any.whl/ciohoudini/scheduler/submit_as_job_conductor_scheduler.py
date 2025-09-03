import os
import json
import traceback
import pdg
import hou
import socket
import datetime
import time
import shutil
import re
import logging

from ciohoudini import (
    job_title,
    project,
    instances,
    software,
    environment,
    frames,
    task,
    assets,
    rops,
    submit,
    controller,
)

from ciohoudini.submission_dialog import SubmissionDialog
from ciocore import conductor_submit
from ciocore import data as coredata
from ciohoudini.scheduler.pdg_utils import connect_to_conductor, get_hhp_dir

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler if logger doesn't have handlers
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


class PDGConductorSubmitAsJob:
    """PDG Conductor Submit As Job for submitting entire TOP networks to Conductor"""

    def __init__(self, scheduler_context, node_path=None):
        """Initialize the submitter with context

        Args:
            scheduler_context: The PDG scheduler context (self from the original script)
        """
        self.context = scheduler_context
        self.working_dir = None
        self.script_dir = None
        self.temp_dir = None
        self.render_dir = None
        self.usd_dir = None
        self.geo_dir = None
        self.render_output_dir = None
        self.images_dir = None
        self.node = None
        self.node_path = node_path
        if self.node_path:
            self.node = hou.node(node_path)

    def get_local_ip(self):
        """Try to get the local machine's IP address that's accessible from the network"""
        try:
            # Method 1: Connect to an external server and get the local address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            try:
                # Method 2: Get hostname and resolve it
                hostname = socket.gethostname()
                return socket.gethostbyname(hostname)
            except:
                # Fallback - you should replace this with your actual IP
                return "192.168.1.100"  # REPLACE WITH ACTUAL IP

    def validate_and_clean_path(self, path):
        """Validate and clean a path for Conductor submission

        Args:
            path: The path to validate

        Returns:
            str or None: Cleaned absolute path or None if invalid
        """
        try:
            # Skip empty paths
            if not path:
                return None

            # Convert to string if needed
            path = str(path)

            # Skip paths with problematic characters for Conductor
            # Check for multiple colons (except for Windows drive letters)
            colon_count = path.count(':')
            if colon_count > 1 or (colon_count == 1 and not (len(path) > 2 and path[1] == ':')):
                logger.warning(f"Skipping path with invalid colons: {path}")
                return None

            # Make path absolute
            if not os.path.isabs(path):
                path = os.path.abspath(path)

            # Normalize the path
            path = os.path.normpath(path)

            # Check if path exists
            if not os.path.exists(path):
                logger.warning(f"Path does not exist: {path}")
                return None

            # Check for circular symlinks or other issues
            try:
                real_path = os.path.realpath(path)
                if real_path != path:
                    logger.debug(f"Resolved symlink {path} -> {real_path}")
                    path = real_path
            except Exception as e:
                logger.warning(f"Could not resolve path {path}: {e}")
                return None

            return path

        except Exception as e:
            logger.warning(f"Error validating path {path}: {e}")
            return None

    def get_next_version_number(self, base_path):
        """Get the next available version number for the hip file

        Args:
            base_path: The base path (e.g., "/path/to/file.hip" or "/path/to/file_pdg_v0001.hip")

        Returns:
            int: The next available version number
        """
        dir_path = os.path.dirname(base_path)
        base_name_with_ext = os.path.basename(base_path)
        base_name = os.path.splitext(base_name_with_ext)[0]

        # Check if the file already has a version pattern and extract the base name
        existing_version_match = re.match(r"(.*)_pdg_v(\d{4})$", base_name)
        if existing_version_match:
            # File already has version, extract the base name without version
            clean_base_name = existing_version_match.group(1)
            current_version = int(existing_version_match.group(2))
        else:
            # File doesn't have version yet
            clean_base_name = base_name
            current_version = 0

        # Pattern to match existing versioned files with this base name
        pattern = f"{re.escape(clean_base_name)}_pdg_v(\\d{{4}})\\.hip"

        max_version = current_version

        # Check if directory exists and scan for existing versions
        if os.path.exists(dir_path):
            for filename in os.listdir(dir_path):
                match = re.match(pattern, filename)
                if match:
                    version = int(match.group(1))
                    max_version = max(max_version, version)

        # Return the next version number
        return max_version + 1

    def create_versioned_hip_filename(self, original_hip_path):
        """Create a versioned hip filename based on the original path

        Args:
            original_hip_path: The original hip file path

        Returns:
            str: The versioned hip file path
        """
        dir_path = os.path.dirname(original_hip_path)
        base_name_with_ext = os.path.basename(original_hip_path)
        base_name = os.path.splitext(base_name_with_ext)[0]

        # Check if the file already has a version pattern
        existing_version_match = re.match(r"(.*)_pdg_v(\d{4})$", base_name)
        if existing_version_match:
            # File already has version, use the clean base name
            clean_base_name = existing_version_match.group(1)
        else:
            # File doesn't have version yet, use the full base name
            clean_base_name = base_name

        # Get the next version number using the clean base name
        next_version = self.get_next_version_number(original_hip_path)

        # Create the versioned filename
        versioned_filename = f"{clean_base_name}_pdg_v{next_version:04d}.hip"
        versioned_path = os.path.join(dir_path, versioned_filename)

        logger.debug(f"Original hip file: {original_hip_path}")
        logger.debug(f"Versioned hip file: {versioned_path}")
        logger.debug(f"Version number: {next_version}")

        return versioned_path

    def prepare_submit_as_job(self, graph_file, node_path):
        """Prepare a submit as job submission

        Args:
            graph_file: Path to a .hip file containing the TOP Network
            node_path: Op path to the TOP Network

        Returns:
            tuple: (task_data, upload_paths, job_title, job_env)
        """
        logger.info("╔══════════════════════════════════════════════════════════╗")
        logger.info("║              PREPARING SUBMIT AS JOB                      ║")
        logger.info(f"║  Graph File: {graph_file}           ║")
        logger.info(f"║  Node Path: {node_path}             ║")
        logger.info("╚══════════════════════════════════════════════════════════╝")

        # Collect upload paths - ensure all are absolute
        all_upload_paths = set()

        # Get the HIP folder from $HIP:
        hip_file_dir = os.path.dirname(hou.hipFile.path()) if hou.hipFile.path() else os.getcwd()
        self.script_dir = os.path.join(hip_file_dir, "pdg")
        self.working_dir = hip_file_dir
        self.script_dir = os.path.join(self.working_dir, "scripts")
        self.temp_dir = os.path.join(self.working_dir, "temp")

        all_upload_paths.add(self.working_dir)
        all_upload_paths.add(self.script_dir)
        all_upload_paths.add(self.temp_dir)

        logger.debug("Initial upload paths:")
        for path in all_upload_paths:
            logger.debug(f"  - {path}")

        # Create common directories with absolute paths
        self.render_dir = os.path.abspath(os.path.join(self.working_dir, "execute", "pdg_render"))
        self.usd_dir = os.path.abspath(os.path.join(self.working_dir, "usd"))
        self.geo_dir = os.path.abspath(os.path.join(self.working_dir, "geo"))
        self.render_output_dir = os.path.abspath(os.path.join(self.working_dir, "render"))
        self.images_dir = os.path.abspath(os.path.join(self.working_dir, "images"))

        for dir_path in [self.usd_dir, self.geo_dir, self.render_output_dir, self.images_dir]:
            all_upload_paths.add(dir_path)
        for dir_path in [self.render_dir, self.usd_dir, self.geo_dir, self.render_output_dir, self.images_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.debug(f"Created directory: {dir_path}")

        # Handle the hip file
        if graph_file and os.path.exists(graph_file):
            # Use provided graph file
            hip_file_path = self.create_versioned_hip_filename(graph_file)
            # Copy the graph file to the versioned location
            shutil.copy2(graph_file, hip_file_path)
            logger.debug(f"Copied graph file to versioned location: {hip_file_path}")
        else:
            # Use current hip file
            current_hip_path = hou.hipFile.path()
            hip_file_path = self.create_versioned_hip_filename(current_hip_path)
            # Save current hip file with version
            logger.debug(f"Saving versioned hip file for farm: {hip_file_path}")
            hou.hipFile.save(hip_file_path)

        # Ensure hip file path is absolute
        hip_file_path = os.path.abspath(hip_file_path)
        all_upload_paths.add(hip_file_path)

        # Define the wrapper script path
        wrapper_script_source = rops.get_parameter_value(self.node, "render_script")

        if not wrapper_script_source:
            cio_dir = os.environ.get("CIODIR")
            if cio_dir:
                wrapper_script_source = os.path.join(cio_dir, "ciohoudini", "scheduler", "pdg_universal_wrapper.py")
            else:
                logger.warning("CIODIR environment variable is not set. Cannot determine wrapper script path.")
                wrapper_script_source = ""

        if wrapper_script_source and not os.path.exists(wrapper_script_source):
            logger.warning(f"Wrapper script not found at {wrapper_script_source}. Falling back to default if available.")

        # If the wrapper doesn't exist, create a basic one
        if not os.path.exists(wrapper_script_source):
            # Create a temporary wrapper script with absolute path
            wrapper_dir = os.path.abspath(os.path.join(self.working_dir, "scripts"))
            if not os.path.exists(wrapper_dir):
                os.makedirs(wrapper_dir, exist_ok=True)
            wrapper_script_source = os.path.abspath(os.path.join(wrapper_dir, "pdg_universal_wrapper.py"))

            # Write a basic wrapper script
            wrapper_content = '''#!/usr/bin/env python3
import sys
import os
import argparse
import traceback

def main():
    parser = argparse.ArgumentParser(description='PDG Submit As Job Wrapper')
    parser.add_argument('--hip_file', required=True, help='Path to HIP file')
    parser.add_argument('--topnet_path', required=True, help='Path to TOP network')
    parser.add_argument('--working_dir', required=True, help='Working directory')
    #parser.add_argument('--cook_entire_graph', action='store_true', help='Cook entire graph')

    args = parser.parse_args()

    try:
        # Import Houdini
        import hou

        # Load the hip file
        print(f"Loading HIP file: {args.hip_file}")
        hou.hipFile.load(args.hip_file)

        # Get the TOP network
        print(f"Getting TOP network: {args.topnet_path}")
        topnet = hou.node(args.topnet_path)
        if not topnet:
            raise ValueError(f"Could not find TOP network at: {args.topnet_path}")

        # Cook the TOP network
        print(f"Cooking TOP network...")
        if hasattr(topnet, 'cookWorkItems'):
            topnet.cookWorkItems(block=True)
        else:
            # Alternative method for older versions
            for node in topnet.children():
                if hasattr(node, 'cook'):
                    node.cook(force=True)

        print("Successfully cooked TOP network")
        return 0

    except Exception as e:
        print(f"Error in wrapper script: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
            with open(wrapper_script_source, 'w') as f:
                f.write(wrapper_content)
            os.chmod(wrapper_script_source, 0o755)
            logger.debug(f"Created temporary wrapper script: {wrapper_script_source}")
        else:
            # Ensure the existing wrapper path is absolute
            wrapper_script_source = os.path.abspath(wrapper_script_source)

        all_upload_paths.add(wrapper_script_source)

        # Create task command for submit as job
        task_command = f'hython {wrapper_script_source} --hip_file "{hip_file_path}" --topnet_path "{node_path}" --working_dir "{self.working_dir}" --output_dir "{self.render_dir}" --cook_entire_graph'

        # Get HIP filename for job title
        hip_filename = os.path.splitext(os.path.basename(hip_file_path))[0]
        job_title = f"PDG_SubmitAsJob_{node_path.split('/')[-1]}_{hip_filename}"
        task_data = [
            {
                "name": f"PDG_Cook_{node_path.split('/')[-1]}",
                "command": task_command,
                "frames": "1"
            },
            {
                "name": f"PDG_Cook_{node_path.split('/')[-1]}",
                "command": task_command,
                "frames": "2"
            },
            {
                "name": f"PDG_Cook_{node_path.split('/')[-1]}",
                "command": task_command,
                "frames": "3"
            }
        ]

        # Build environment variables
        job_env = self.build_job_environment()

        logger.debug("Submit as job summary:")
        logger.debug(f"  Title: {job_title}")
        logger.debug(f"  Node Path: {node_path}")
        logger.debug(f"  Hip File: {hip_file_path}")
        logger.debug(f"  Upload paths before validation: {len(all_upload_paths)}")

        # Validate and clean all upload paths
        final_upload_paths = []
        for p in all_upload_paths:
            cleaned_path = self.validate_and_clean_path(p)
            if cleaned_path:
                final_upload_paths.append(cleaned_path)

        logger.debug(f"  Upload paths after validation: {len(final_upload_paths)}")

        # Remove duplicates while preserving order
        seen = set()
        unique_upload_paths = []
        for path in final_upload_paths:
            if path not in seen:
                seen.add(path)
                unique_upload_paths.append(path)

        logger.debug(f"  Unique upload paths: {len(unique_upload_paths)}")

        return task_data, unique_upload_paths, job_title, job_env

    def build_job_environment(self):
        """Build the environment variables for the submit as job

        Args:
            render_dir: The render directory path

        Returns:
            dict: Environment variables for the job
        """
        # Try to get the result server address
        result_server_addr = ""
        try:
            if hasattr(self.context, 'workItemResultServerAddr'):
                result_server_addr = str(self.context.workItemResultServerAddr())
                logger.debug(f"Original result server address: {result_server_addr}")
            else:
                logger.debug("No workItemResultServerAddr available")
        except Exception as e:
            logger.debug(f"Could not get result server address: {e}")
            result_server_addr = ""

        # Handle result server address
        if result_server_addr and ":" in result_server_addr:
            if result_server_addr.startswith("127.0.0.1:"):
                # This is a localhost address that won't work from the farm
                parts = result_server_addr.split(":")
                if len(parts) >= 2:
                    port = parts[1]
                    local_ip = self.get_local_ip()
                    result_server_addr = f"{local_ip}:{port}"
                    logger.debug(f"Replaced localhost with machine IP: {result_server_addr}")

            if ":" in result_server_addr:
                port = result_server_addr.split(':')[1]
                logger.debug(f"PDG Result Server: {result_server_addr}")
                logger.debug(f"Make sure firewall allows incoming connections on port {port}")
        else:
            # No valid result server address, use a default or skip
            logger.warning("No valid result server address available")
            logger.warning("Submit as job may not report results back properly")
            # Set a placeholder or leave empty
            result_server_addr = ""

        # Build base environment
        job_env = {
            "PDG_RESULT_SERVER": result_server_addr,
            "PDG_DIR": self.working_dir,
            "PDG_TEMP": self.temp_dir,
            "PDG_SCRIPTDIR": self.script_dir,
            "PDG_RENDER_DIR": self.render_dir,
            "PDG_RPC_TIMEOUT": "60",
            "PDG_RPC_MAX_ERRORS": "20",
            "PDG_RPC_BATCH": "1",
            "PDG_RPC_RETRY_DELAY": "5",
            "PDG_RPC_IGNORE_WORK_ITEM_RESULTS": "0",
            "PDG_SUBMIT_AS_JOB": "1",  # Flag to indicate this is a submit as job
            "HOUDINI_TEMP_DIR": self.temp_dir,
        }

        # Only add PDG_RESULT_SERVER if we have a valid address
        if result_server_addr:
            job_env["PDG_RESULT_SERVER"] = result_server_addr

        if self.node:
            conductor_env = environment.resolve_payload(self.node)
            conductor_env = conductor_env.get("environment", {})
            job_env.update(conductor_env)

        for key in ["JOB", "OCIO"]:
            job_env.pop(key, None)

        # Check if HHP is missing and add it if needed
        if "HHP" not in job_env:
            hfs = job_env.get("HFS", '/opt/sidefx/houdini/20/houdini-20.5.522-gcc11.2')
            hhp_dir = get_hhp_dir(hfs)
            job_env["HHP"] = hhp_dir
            logger.debug(f"Added HHP: {hhp_dir}")

        logger.debug("Job environment:")
        for key, value in job_env.items():
            logger.debug(f"  {key}: {value}")

        return job_env

    def submit_job_to_conductor(self, job_spec):
        """Submit the job to Conductor

        Args:
            job_spec: The job specification dictionary

        Returns:
            pdg.scheduleResult: The scheduling result
        """
        logger.debug("╔══════════════════════════════════════════════════════════╗")
        logger.debug("║                  JOB SPECIFICATION:                       ║")
        logger.debug("╚══════════════════════════════════════════════════════════╝")
        logger.debug(json.dumps(job_spec, indent=2))
        logger.debug("╚══════════════════════════════════════════════════════════╝")

        logger.info("Submitting to Conductor...")
        submission_start = time.time()

        try:
            # Implement this
            use_submission_dialog = False

            if use_submission_dialog:
                import hdefereval

                def show_dialog():
                    try:
                        nodes = [self.node] if self.node else []
                        payloads = [job_spec]
                        submission_dialog = SubmissionDialog(nodes, payloads=payloads)
                        submission_dialog.exec_()
                    except Exception as e:
                        logger.error(f"Dialog error: {e}")

                hdefereval.executeInMainThreadWithResult(show_dialog)
            else:
                remote_job = conductor_submit.Submit(job_spec)
                response, code = remote_job.main()
                submission_end = time.time()

                logger.debug(f"Conductor response received in {submission_end - submission_start:.2f} seconds")
                logger.debug(f"Response code: {code}")
                logger.debug(f"Response: {json.dumps(response, indent=2)}")

                if code in (200, 201):
                    job_id = response.get("jobid")
                    if job_id:
                        logger.info("╔══════════════════════════════════════════════════════════╗")
                        logger.info("║                    JOB SUBMITTED SUCCESSFULLY            ║")
                        logger.info(f"║  Job ID: {job_id:<48}║")
                        logger.info("╚══════════════════════════════════════════════════════════╝")

                        # Store the job ID in scheduler attributes if needed
                        if hasattr(self.context, 'setStringAttrib'):
                            self.context.setStringAttrib("conductor_submitasjob_id", job_id)

                        return pdg.scheduleResult.Succeeded
                    else:
                        logger.error(f"No job ID in response: {response}")
                        return pdg.scheduleResult.Failed
                else:
                    logger.error(f"Submission failed, code: {code}, response: {response}")
                    return pdg.scheduleResult.Failed

        except ImportError as e:
            logger.error(f"ImportError for ciocore: {traceback.format_exc()}")
            return pdg.scheduleResult.Failed
        except Exception as e:
            logger.error(f"Exception submitting job: {traceback.format_exc()}")
            return pdg.scheduleResult.Failed

    def execute(self, graph_file, node_path):
        """Main execution function for submit as job

        Args:
            graph_file: Path to a .hip file containing the TOP Network
            node_path: Op path to the TOP Network

        Returns:
            pdg.scheduleResult: The scheduling result
        """
        logger.info("Custom submitAsJob (Conductor version)")
        logger.debug(f"Script started at: {datetime.datetime.now()}")
        logger.debug(f"Graph file: {graph_file}")
        logger.debug(f"Node path: {node_path}")

        try:
            # Validate inputs
            if not node_path:
                logger.error("No node path provided")
                return pdg.scheduleResult.Failed

            # If graph_file is provided, validate it exists
            if graph_file and not os.path.exists(graph_file):
                logger.warning(f"Graph file does not exist: {graph_file}")
                logger.warning("Will use current hip file instead")
                graph_file = None

            # Connect to Conductor and ensure connection is valid
            try:
                connect_to_conductor(self.node)
            except RuntimeError as e:
                logger.error(f"Failed to establish Conductor connection: {e}")
                return pdg.scheduleResult.Failed
            except Exception as e:
                logger.error(f"Unexpected error connecting to Conductor: {e}")
                return pdg.scheduleResult.Failed

            # Prepare the submit as job
            tasks_data, upload_paths, job_title, job_env = self.prepare_submit_as_job(
                graph_file, node_path
            )

            # Build job environment
            kwargs = {
                "do_asset_scan": True,
                "task_limit": -1
            }
            frame_range_to_use = self.node.parm("frame_range").evalAsString()
            job_env = self.build_job_environment()

            project_name = project.resolve_payload(self.node)
            project_name = project_name.get("project", "default")

            instance_type = instances.resolve_payload(self.node)
            instance_type = instance_type.get("instance_type", "")

            software_package_ids = software.resolve_payload(self.node)
            software_package_ids = software_package_ids.get("software_package_ids", [])

            scout_frames = frames.resolve_payload(self.node, frame_range=frame_range_to_use)
            scout_frames = scout_frames.get("scout_frames", "1")

            upload_paths_conductor = assets.resolve_payload(self.node, **kwargs)
            upload_paths_conductor = upload_paths_conductor.get("upload_paths", [])
            upload_paths = list(set(upload_paths + upload_paths_conductor))

            # Create job specification
            job_spec = {
                "job_title": job_title,
                "project": project_name,
                "instance_type": instance_type,
                "preemptible": False,
                "autoretry_policy": {"preempted": {"max_retries": 2}},
                "software_package_ids": software_package_ids,
                "environment": job_env,
                "output_path": self.render_dir,
                "local_upload": True,
                "scout_frames": scout_frames,
                "tasks_data": tasks_data,
                "upload_paths": upload_paths,
            }

            logger.debug("Resolved job_spec:")
            for key, value in job_spec.items():
                logger.debug(f"  {key}: {value}")

            # Submit job to Conductor
            return self.submit_job_to_conductor(job_spec)

        except Exception as e:
            logger.error("╔══════════════════════════════════════════════════════════╗")
            logger.error("║              CRITICAL ERROR IN submitAsJob                ║")
            logger.error("╚══════════════════════════════════════════════════════════╝")
            logger.error(traceback.format_exc())
            logger.error("╚══════════════════════════════════════════════════════════╝")
            return pdg.scheduleResult.Failed


def submitAsJob(self, graph_file, node_path):
    # Custom submitAsJob logic. Returns the status URI for the submitted job.
    #
    # The following variables are available:
    # self          -  A reference to the current pdg.Scheduler instance
    # graph_file    -  Path to a .hip file containing the TOP Network, relative to $PDGDIR.
    # node_path     -  Op path to the TOP Network

    # from ciohoudini.scheduler.submit_as_job_conducor_scheduler import PDGConductorSubmitAsJob
    #logger = logging.getLogger(__name__)
    #logger.setLevel(logging.DEBUG)

    logger.debug(f"node_path is {node_path}")
    logger.debug(f"graph_file is {graph_file}")

    scheduler_name = self.name
    logger.debug(f"self.name is {self.name}")
    topnet_hou_node = hou.node(node_path)

    scheduler_node = None
    for node in topnet_hou_node.allSubChildren():
        if (node.type().name() == "conductorscheduler" and
                node.name() == scheduler_name):
            scheduler_node = node
            scheduler_path = scheduler_node.path()
            break
    logger.debug(f"scheduler_path is {scheduler_path}")

    if scheduler_node and scheduler_path:
        submitter = PDGConductorSubmitAsJob(self, node_path=scheduler_path)
        submitter.execute(graph_file, node_path)