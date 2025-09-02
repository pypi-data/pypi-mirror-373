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
import hdefereval
import logging
from ciohoudini import (
    job_title,
    project,
    instances,
    software,
    environment,
    driver,
    frames,
    task,
    assets,
    miscellaneous,
    render_rops,
    rops,
    util,
    submit,
)
from ciohoudini.submission_dialog import SubmissionDialog
from ciohoudini.scheduler.pdg_utils import connect_to_conductor, get_hhp_dir, configure_threading_environment

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler if it doesn't exist
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


class PDGConductorScheduler:
    """PDG Conductor Scheduler for managing work item submission to Conductor"""

    def __init__(self, scheduler_context, node_path=None, node=None):
        """Initialize the scheduler with context

        Args:
            scheduler_context: The PDG scheduler context (self from the original script)
        """
        self.context = scheduler_context
        if node_path:
            self.node = hou.node(node_path)
        else:
            self.node = node

    def save_hip_file_safe(self, hip_file_path):
        """Thread-safe method to save HIP file

        Args:
            hip_file_path: Path where to save the HIP file

        Returns:
            bool: True if successful, False otherwise
        """

        def save_hip():
            try:
                hou.hipFile.save(hip_file_path)
                return True
            except Exception as e:
                logger.error(f"ERROR saving HIP file: {e}")
                return False

        # Check if we're already on the main thread
        if hou.isUIAvailable():
            # We need to use the main thread for GUI operations
            try:
                result = hdefereval.executeInMainThreadWithResult(save_hip)
                return result
            except Exception as e:
                logger.error(f"ERROR in executeInMainThreadWithResult: {e}")
                # Fallback: try saving directly if hdefereval fails
                try:
                    return save_hip()
                except:
                    return False
        else:
            # In batch mode (no UI), save directly
            return save_hip()

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
                logger.warning("Could not determine local IP, using fallback 192.168.1.100")
                return "192.168.1.100"  # REPLACE WITH YOUR ACTUAL IP

    def get_topnet_path(self, pdg_node):
        """Get the path to the TOP network containing this PDG node"""
        topnode = pdg_node.topNode().parent()
        if topnode:
            return topnode.path()
        return None

    def log_work_item_details(self, work_item, level=logging.DEBUG):
        """Log detailed information about a work item"""
        logger.log(level, "────────────────────────────────────────────────────────────")
        logger.log(level, "Work Item Details:")
        logger.log(level, f"  Name: {work_item.name}")
        logger.log(level, f"  ID: {work_item.id}")
        logger.log(level, f"  Index: {work_item.index}")

        # Safely get state
        try:
            state = str(work_item.state) if hasattr(work_item, 'state') else 'unknown'
            logger.log(level, f"  State: {state}")
        except:
            logger.warning("  State: <error reading state>")

        logger.log(level, f"  Node: {work_item.node.name}")

        # Safely get cook type
        try:
            cook_type = str(work_item.cookType) if hasattr(work_item, 'cookType') else 'unknown'
            logger.log(level, f"  Cook Type: {cook_type}")
        except:
            logger.warning("  Cook Type: <error reading cook type>")

        # Safely get boolean properties
        try:
            is_static = work_item.isStatic if hasattr(work_item, 'isStatic') else 'unknown'
            logger.log(level, f"  Is Static: {is_static}")
        except:
            logger.warning("  Is Static: <error>")

        try:
            is_frozen = work_item.isFrozen if hasattr(work_item, 'isFrozen') else 'unknown'
            logger.log(level, f"  Is Frozen: {is_frozen}")
        except:
            logger.warning("  Is Frozen: <error>")

        try:
            priority = work_item.priority if hasattr(work_item, 'priority') else 'unknown'
            logger.log(level, f"  Priority: {priority}")
        except:
            logger.warning("  Priority: <error>")

        try:
            has_frame = work_item.hasFrame if hasattr(work_item, 'hasFrame') else False
            logger.log(level, f"  Has Frame: {has_frame}")
            if has_frame:
                logger.log(level, f"  Frame: {work_item.frame}")
        except:
            logger.warning("  Has Frame: <error>")

        # Log attributes
        logger.log(level, "  Attributes:")
        try:
            for attr_name in work_item.attribNames():
                try:
                    # Try different methods to get attribute value
                    if hasattr(work_item, 'stringAttribValue'):
                        # Try string first as it's most common
                        attr_value = work_item.stringAttribValue(attr_name)
                        if attr_value:
                            logger.log(level, f"    {attr_name}: {attr_value}")
                            continue

                    # Try generic attribValue
                    if hasattr(work_item, 'attribValue'):
                        attr_value = work_item.attribValue(attr_name)
                        logger.log(level, f"    {attr_name}: {attr_value}")
                    else:
                        logger.warning(f"    {attr_name}: <no attribValue method>")
                except:
                    logger.warning(f"    {attr_name}: <unable to read>")
        except Exception as e:
            logger.error(f"  [ERROR] Could not get attribute names: {str(e)}")

        # Log dependencies
        try:
            dependencies = work_item.dependencies if hasattr(work_item, 'dependencies') else []
            if dependencies:
                logger.log(level, f"  Dependencies ({len(dependencies)}):")
                for dep in dependencies:
                    dep_state = str(dep.state) if hasattr(dep, 'state') else 'unknown'
                    logger.log(level, f"    - {dep.name} (ID: {dep.id}, State: {dep_state})")
        except Exception as e:
            logger.error(f"  [ERROR] Could not get dependencies: {str(e)}")

        # Log dependents
        try:
            dependents = work_item.dependents if hasattr(work_item, 'dependents') else []
            if dependents:
                logger.log(level, f"  Dependents ({len(dependents)}):")
                for dep in dependents:
                    dep_state = str(dep.state) if hasattr(dep, 'state') else 'unknown'
                    logger.log(level, f"    - {dep.name} (ID: {dep.id}, State: {dep_state})")
        except Exception as e:
            logger.error(f"  [ERROR] Could not get dependents: {str(e)}")

        logger.log(level, "────────────────────────────────────────────────────────────")

    def log_node_details(self, node, level=logging.DEBUG):
        """Log detailed information about a PDG node"""
        logger.log(level, "┌────────────────────────────────────────────────────────────┐")
        logger.log(level, "│ PDG Node Details:                                            │")
        logger.log(level, "├────────────────────────────────────────────────────────────┤")
        logger.log(level, f"│ Name: {node.name:<54} │")

        # Safely get node type
        try:
            node_type = node.type.name if hasattr(node, 'type') and hasattr(node.type, 'name') else 'unknown'
            logger.log(level, f"│ Type: {node_type:<54} │")
        except:
            logger.warning("│ Type: <unknown>                                             │")

        # Safely get node path
        try:
            hou_node = node.houdiniNode if hasattr(node, 'houdiniNode') else None
            node_path = hou_node.path() if hou_node else 'N/A'
            # Truncate if too long
            if len(node_path) > 54:
                node_path = node_path[:51] + "..."
            logger.log(level, f"│ Path: {node_path:<54} │")
        except:
            logger.warning("│ Path: <not available>                                       │")

        # Safely get node state
        try:
            node_state = str(node.state) if hasattr(node, 'state') else 'unknown'
            logger.log(level, f"│ State: {node_state:<53} │")
        except:
            logger.warning("│ State: <unknown>                                            │")

        # Safely get work item counts
        try:
            wi_count = len(node.workItems) if hasattr(node, 'workItems') else 0
            logger.log(level, f"│ Work Item Count: {wi_count:<43} │")
        except:
            logger.warning("│ Work Item Count: <error>                                    │")

        try:
            static_wi_count = len(node.staticWorkItems) if hasattr(node, 'staticWorkItems') else 0
            logger.log(level, f"│ Static Work Items: {static_wi_count:<41} │")
        except:
            logger.warning("│ Static Work Items: <error>                                  │")

        # Safely get boolean states
        try:
            is_cooking = str(node.isCooking) if hasattr(node, 'isCooking') else 'unknown'
            logger.log(level, f"│ Is Cooking: {is_cooking:<48} │")
        except:
            logger.warning("│ Is Cooking: <unknown>                                       │")

        try:
            is_generated = str(node.isGenerated) if hasattr(node, 'isGenerated') else 'unknown'
            logger.log(level, f"│ Is Generated: {is_generated:<46} │")
        except:
            logger.warning("│ Is Generated: <unknown>                                     │")

        try:
            is_cooked = str(node.isCooked) if hasattr(node, 'isCooked') else 'unknown'
            logger.log(level, f"│ Is Cooked: {is_cooked:<49} │")
        except:
            logger.warning("│ Is Cooked: <unknown>                                        │")

        logger.log(level, "└────────────────────────────────────────────────────────────┘")

    def log_pdg_graph_state(self, work_item, level=logging.DEBUG):
        """Log the entire PDG graph state"""
        logger.log(level, "╔═════════════════════════════════════════════════════════════╗")
        logger.log(level, "║                    PDG GRAPH STATE SNAPSHOT                    ║")
        logger.log(level,
                   f"║                 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}                 ║")
        logger.log(level, "╚═════════════════════════════════════════════════════════════╝")

        # Get the graph context
        graph = work_item.node.context
        logger.log(level, f"Graph Name: {graph.name}")

        # Try to get graph info
        try:
            graph_hou_node = graph.houdiniNode if hasattr(graph, 'houdiniNode') else None
            graph_path = graph_hou_node.path() if graph_hou_node else '<not available>'
            logger.log(level, f"Graph Path: {graph_path}")
        except:
            logger.warning("Graph Path: <not available>")

        # Iterate through all nodes in the graph
        all_nodes = []
        try:
            # Different ways to get nodes depending on PDG version
            if hasattr(graph, 'nodes'):
                for node in graph.nodes:
                    all_nodes.append(node)
            elif hasattr(graph, 'nodeByName'):
                # Alternative: try to get nodes through the current node's graph
                current_node = work_item.node
                # This is a workaround - we'll just log the current node and its connections
                logger.debug("[INFO] Using alternative node discovery method")
                all_nodes = [current_node]

                # Try to find connected nodes through dependencies
                processed_nodes = set()
                nodes_to_process = [current_node]

                while nodes_to_process:
                    node = nodes_to_process.pop(0)
                    if node.name in processed_nodes:
                        continue
                    processed_nodes.add(node.name)

                    # Get dependencies and dependents
                    for wi in node.workItems:
                        for dep in wi.dependencies:
                            if dep.node not in all_nodes and dep.node.name not in processed_nodes:
                                all_nodes.append(dep.node)
                                nodes_to_process.append(dep.node)
                        for dep in wi.dependents:
                            if dep.node not in all_nodes and dep.node.name not in processed_nodes:
                                all_nodes.append(dep.node)
                                nodes_to_process.append(dep.node)
        except Exception as e:
            logger.warning(f"[WARNING] Could not iterate nodes: {str(e)}")
            # Fallback to just the current node
            all_nodes = [work_item.node]

        logger.log(level, f"Total Nodes Found: {len(all_nodes)}")
        logger.log(level, "")

        # Log each node's state
        for idx, node in enumerate(all_nodes):
            logger.log(level, f"Node [{idx + 1}/{len(all_nodes)}]:")
            self.log_node_details(node, level)

            # Log work items for this node
            try:
                work_items = node.workItems
                if work_items:
                    logger.log(level, f"  Work Items ({len(work_items)}):")
                    for wi_idx, wi in enumerate(work_items[:5]):  # Limit to first 5 for brevity
                        state_str = str(wi.state) if hasattr(wi, 'state') else 'unknown'
                        logger.log(level, f"    [{wi_idx + 1}] {wi.name} - State: {state_str}, ID: {wi.id}")
                    if len(work_items) > 5:
                        logger.log(level, f"    ... and {len(work_items) - 5} more work items")
            except Exception as e:
                logger.error(f"  [ERROR] Could not get work items: {str(e)}")
            logger.log(level, "")

    def check_first_to_schedule(self, work_item):
        """Check if this is the first work item to be scheduled

        Args:
            work_item: The current work item

        Returns:
            bool: True if first to schedule, False otherwise
        """
        logger.debug("Checking if this is the first work item to be scheduled...")
        first_to_schedule = True

        current_node_work_items = work_item.node.workItems
        logger.debug(f"Current node ({work_item.node.name}) has {len(current_node_work_items)} work items")

        for wi in current_node_work_items:
            logger.debug(f"  Checking work item: {wi.name} (ID: {wi.id})")
            conductor_batch_id = wi.stringAttribValue("conductor_batch_job_id")
            logger.debug(f"    conductor_batch_job_id: {conductor_batch_id}")

            if wi != work_item and conductor_batch_id:
                first_to_schedule = False
                logger.debug(f"    Found already scheduled item, not first to schedule")
                break

        logger.debug(f"Is first to schedule: {first_to_schedule}")
        return first_to_schedule

    def collect_work_items_for_batch(self, work_item):
        """Collect all work items from the node that are ready to be scheduled

        Args:
            work_item: The current work item

        Returns:
            list: List of work items ready for batching
        """
        work_item_chain = []
        current_node_work_items = work_item.node.workItems

        logger.info(f"First to schedule - collecting all ready items from node {work_item.node.name}")

        for wi in current_node_work_items:
            logger.debug(f"  Evaluating work item: {wi.name} (ID: {wi.id}, State: {wi.state})")

            # Check if work item is ready (not already submitted)
            conductor_batch_id = wi.stringAttribValue("conductor_batch_job_id")
            logger.debug(f"    conductor_batch_job_id: {conductor_batch_id}")

            if not conductor_batch_id:
                logger.debug(f"    Adding {wi.name} to work_item_chain")
                work_item_chain.append(wi)

                # Log dependencies
                deps = wi.dependencies
                if deps:
                    logger.debug(f"    Dependencies for {wi.name}:")
                    for dep in deps:
                        logger.debug(f"      - {dep.name} (State: {dep.state})")
            else:
                logger.debug(f"    Skipping {wi.name} - already has batch job ID")

        return work_item_chain

    def prepare_batch_job(self, work_item_chain, topnet_path, wrapper_script_source):
        """Prepare a batch job with multiple work items

        Args:
            work_item_chain: List of work items to batch
            topnet_path: Path to the TOP network
            wrapper_script_source: Path to the wrapper script

        Returns:
            tuple: (tasks_data, upload_paths, job_title)
        """
        logger.info("╔═════════════════════════════════════════════════════════════╗")
        logger.info("║              CREATING BATCH JOB                            ║")
        logger.info(f"║              Tasks: {len(work_item_chain):<39}║")
        logger.info("╚═════════════════════════════════════════════════════════════╝")

        # Get the multiple_machines parameter
        use_multiple_machines = rops.get_parameter_value(self.node, "multiple_machines")
        logger.debug(f"Use multiple machines: {use_multiple_machines}")

        # Mark all items as pending
        for idx, item in enumerate(work_item_chain):
            logger.debug(f"Marking item {idx + 1}/{len(work_item_chain)} as pending: {item.name}")
            item.setStringAttrib("conductor_batch_job_id", "pending")

        # Collect all upload paths
        all_upload_paths = set()
        all_upload_paths.add(str(self.context.workingDir(False)))
        all_upload_paths.add(str(self.context.scriptDir(False)))
        all_upload_paths.add(str(self.context.tempDir(False)))  # Add temp dir
        all_upload_paths.add(wrapper_script_source)

        # Add the entire pdgtemp directory structure
        pdgtemp_dir = os.path.join(str(self.context.workingDir(False)), "pdgtemp")
        if os.path.exists(pdgtemp_dir):
            all_upload_paths.add(pdgtemp_dir)
            logger.debug(f"Added pdgtemp directory to uploads: {pdgtemp_dir}")

        logger.debug("Initial upload paths:")
        for path in all_upload_paths:
            logger.debug(f"  - {path}")

        # Create common directories
        render_dir = os.path.join(str(self.context.workingDir(False)), "execute", "pdg_render")
        usd_dir = os.path.join(str(self.context.workingDir(False)), "usd")
        geo_dir = os.path.join(str(self.context.workingDir(False)), "geo")
        render_output_dir = os.path.join(str(self.context.workingDir(False)), "render")
        images_dir = os.path.join(str(self.context.workingDir(False)), "images")
        scripts_dir = os.path.join(str(self.context.workingDir(False)), "scripts")
        logs_dir = os.path.join(str(self.context.workingDir(False)), "logs")
        data_dir = os.path.join(str(self.context.workingDir(False)), "data")

        for dir_path in [usd_dir, geo_dir, render_output_dir, images_dir, scripts_dir, logs_dir, data_dir]:
            all_upload_paths.add(dir_path)
        for dir_path in [render_dir, usd_dir, geo_dir, render_output_dir, images_dir, scripts_dir, logs_dir, data_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.debug(f"Created directory: {dir_path}")

        # Save hip file for farm with versioning
        pdg_dir = str(self.context.workingDir(False))
        base_hip_path = os.path.join(pdg_dir, f"pdg_graph_{work_item_chain[0].node.name}.hip")
        hip_file_path = self.create_versioned_hip_filename(base_hip_path)
        logger.info(f"Saving versioned hip file for farm: {hip_file_path}")

        # Use thread-safe save method
        if not self.save_hip_file_safe(hip_file_path):
            logger.error("Failed to save HIP file, aborting batch job preparation")
            raise RuntimeError("Failed to save HIP file")

        all_upload_paths.add(hip_file_path)

        # Create tasks for each work item
        tasks_data = []

        if use_multiple_machines:
            # Original behavior: one work item per machine (frame)
            logger.debug("Creating tasks for multiple machines...")
            for idx, item in enumerate(work_item_chain):
                logger.debug(f"Processing work item {idx + 1}/{len(work_item_chain)}: {item.name}")

                # Debug information
                logger.debug(f"  Debug - Work Item Info:")
                logger.debug(f"    item.name: {item.name}")
                logger.debug(f"    item.node.name: {item.node.name}")
                logger.debug(f"    item.id: {item.id}")
                logger.debug(f"    item.index: {item.index}")

                self.log_work_item_details(item, logging.DEBUG)

                # Serialize this work item
                self.context.createJobDirsAndSerializeWorkItems(item)
                logger.debug(f"  Serialized work item")

                # Add paths from item attributes
                upload_attr = item.stringAttribValue("conductor_upload_paths")
                if upload_attr:
                    logger.debug(f"  Found conductor_upload_paths attribute: {upload_attr}")
                    for p in upload_attr.split(";"):
                        if os.path.exists(p):
                            all_upload_paths.add(p)
                            logger.debug(f"    Added: {p}")

                # Process output files
                self.process_output_files(item, all_upload_paths)

                # Get the actual node name
                actual_node_name = item.node.name

                # Create task command - using item_index for multiple machines
                task_command = f'hython {wrapper_script_source} --hip_file "{hip_file_path}" --topnet_path "{topnet_path}" --item_index {item.index} --working_dir "{str(self.context.workingDir(False))}"'

                task = {
                    "name": f"PDG_{actual_node_name}_{item.name}",
                    "command": task_command,
                    "frames": str(idx + 1),  # Use 1-based frame numbering for multiple machines
                }

                tasks_data.append(task)
                logger.debug(f"  Added task to batch: {task['name']}")
                logger.debug(f"  Task command uses node: {actual_node_name}")
                logger.debug(f"  Frame number: {idx + 1}")

        else:
            # New behavior: all work items to single machine
            logger.info("Creating single task for all work items on one machine...")

            # Serialize all work items
            for idx, item in enumerate(work_item_chain):
                logger.debug(f"Serializing work item {idx + 1}/{len(work_item_chain)}: {item.name}")
                self.context.createJobDirsAndSerializeWorkItems(item)

                # Add paths from item attributes
                upload_attr = item.stringAttribValue("conductor_upload_paths")
                if upload_attr:
                    for p in upload_attr.split(";"):
                        if os.path.exists(p):
                            all_upload_paths.add(p)

                # Process output files
                self.process_output_files(item, all_upload_paths)

            # Create single task command with --use_single_machine flag
            actual_node_name = work_item_chain[0].node.name
            task_command = f'hython {wrapper_script_source} --hip_file "{hip_file_path}" --topnet_path "{topnet_path}" --use_single_machine --working_dir "{str(self.context.workingDir(False))}"'

            task = {
                "name": f"PDG_Batch_{actual_node_name}_SingleMachine",
                "command": task_command,
                "frames": "1",  # Single frame for single machine
            }

            tasks_data.append(task)
            logger.debug(f"  Added single task for all {len(work_item_chain)} work items")
            logger.debug(f"  Task command uses --use_single_machine flag")
            logger.debug(f"  Frame: 1 (single machine execution)")

        # Get versioned HIP filename for job title
        hip_filename = os.path.splitext(os.path.basename(hip_file_path))[0]
        job_title = f"PDG_Batch_{work_item_chain[0].node.name}_{hip_filename}"

        logger.info("Batch job summary:")
        logger.info(f"  Title: {job_title}")
        logger.info(f"  Tasks: {len(tasks_data)}")
        logger.info(f"  Upload paths: {len(all_upload_paths)}")
        logger.info(f"  Mode: {'Multiple machines' if use_multiple_machines else 'Single machine'}")

        return tasks_data, list(all_upload_paths), job_title

    def prepare_single_job(self, work_item, topnet_path, wrapper_script_source):
        """Prepare a single task job

        Args:
            work_item: The work item to process
            topnet_path: Path to the TOP network
            wrapper_script_source: Path to the wrapper script

        Returns:
            tuple: (tasks_data, upload_paths, job_title)
        """
        logger.info("╔═════════════════════════════════════════════════════════════╗")
        logger.info("║              CREATING SINGLE TASK JOB                      ║")
        logger.info("╚═════════════════════════════════════════════════════════════╝")

        # Create common directories
        render_dir = os.path.join(str(self.context.workingDir(False)), "execute", "pdg_render")
        scripts_dir = os.path.join(str(self.context.workingDir(False)), "scripts")
        logs_dir = os.path.join(str(self.context.workingDir(False)), "logs")
        data_dir = os.path.join(str(self.context.workingDir(False)), "data")

        # Collect upload paths
        upload_paths = [
            str(self.context.workingDir(False)),
            str(self.context.scriptDir(False)),
            str(self.context.tempDir(False)),
            wrapper_script_source,
            scripts_dir,
            logs_dir,
            data_dir,
        ]

        # Add the entire pdgtemp directory
        pdgtemp_dir = os.path.join(str(self.context.workingDir(False)), "pdgtemp")
        if os.path.exists(pdgtemp_dir):
            upload_paths.append(pdgtemp_dir)
            logger.debug(f"Added pdgtemp directory to uploads: {pdgtemp_dir}")

        # Create directories if needed
        for dir_path in [render_dir, scripts_dir, logs_dir, data_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.debug(f"Created directory: {dir_path}")

        # Add paths from attributes
        input_attr = work_item.stringAttribValue("conductor_upload_paths")
        if input_attr:
            logger.debug(f"Found conductor_upload_paths: {input_attr}")
            upload_paths.extend([p for p in input_attr.split(";") if os.path.exists(p)])

        # Process output files
        self.process_output_files_single(work_item, upload_paths)

        # Save hip file for farm with versioning
        temp_dir = str(self.context.tempDir(False))
        base_hip_path = os.path.join(temp_dir, f"pdg_graph_{work_item.node.name}.hip")
        hip_file_path = self.create_versioned_hip_filename(base_hip_path)
        logger.info(f"Saving versioned hip file for farm: {hip_file_path}")

        # Use thread-safe save method
        if not self.save_hip_file_safe(hip_file_path):
            logger.error("Failed to save HIP file, aborting single job preparation")
            raise RuntimeError("Failed to save HIP file")

        upload_paths.append(hip_file_path)

        # Create task command
        task_command = f'hython {wrapper_script_source} --hip_file "{hip_file_path}" --topnet_path "{topnet_path}" --item_index {work_item.index} --working_dir "{str(self.context.workingDir(False))}"'

        task = {
            "name": f"PDG_{work_item.node.name}_{work_item.name}",
            "command": task_command,
            "frames": "1"
        }

        tasks_data = [task]

        # Get versioned HIP filename for job title
        hip_filename = os.path.splitext(os.path.basename(hip_file_path))[0]
        job_title = f"PDG_Single_{work_item.node.name}_{hip_filename}"

        logger.debug(f"  Added task to batch: {task['name']}")

        return tasks_data, upload_paths, job_title

    def process_output_files(self, item, upload_paths_set):
        """Process output files for a work item and add to upload paths

        Args:
            item: The work item
            upload_paths_set: Set of upload paths to add to
        """
        logger.debug(f"  Processing output files ({len(item.outputFiles)})...")
        for output_file in item.outputFiles:
            output_path = output_file.path
            logger.debug(f"    Output file: {output_path}")

            # Replace __PDG_DIR__ token if present
            if "__PDG_DIR__" in output_path:
                output_path = output_path.replace("__PDG_DIR__", str(self.context.workingDir(False)))
                logger.debug(f"    Replaced __PDG_DIR__ -> {output_path}")

            output_dir = os.path.dirname(output_path)
            if output_dir:
                upload_paths_set.add(output_dir)
                # Create directory if it doesn't exist
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    logger.debug(f"    Created output directory: {output_dir}")

        # Also check for expected output paths in attributes
        output_attr = item.stringAttribValue("expected_output_path")
        if output_attr:
            logger.debug(f"  Found expected_output_path: {output_attr}")
            # Replace __PDG_DIR__ token if present
            if "__PDG_DIR__" in output_attr:
                output_attr = output_attr.replace("__PDG_DIR__", str(self.context.workingDir(False)))
                logger.debug(f"    Replaced __PDG_DIR__ -> {output_attr}")

            output_dir = os.path.dirname(output_attr)
            if output_dir:
                upload_paths_set.add(output_dir)
                # Create directory if not exist
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    logger.debug(f"    Created expected output directory: {output_dir}")

    def process_output_files_single(self, work_item, upload_paths_list):
        """Process output files for a single work item

        Args:
            work_item: The work item
            upload_paths_list: List of upload paths to add to
        """
        logger.debug(f"Processing output files ({len(work_item.outputFiles)})...")
        for output_file in work_item.outputFiles:
            output_path = output_file.path
            # Replace __PDG_DIR__ token if present
            if "__PDG_DIR__" in output_path:
                output_path = output_path.replace("__PDG_DIR__", str(self.context.workingDir(False)))
            output_dir = os.path.dirname(output_path)
            if output_dir and os.path.exists(output_dir):
                upload_paths_list.append(output_dir)
                logger.debug(f"  Added output directory: {output_dir}")

    def build_job_environment(self, work_item, should_batch, render_dir):
        """Build the environment variables for the job

        Args:
            work_item: The work item
            should_batch: Whether this is a batch job
            render_dir: The render directory path

        Returns:
            dict: Environment variables for the job
        """
        # Get the actual IP address from the result server address
        result_server_addr = str(self.context.workItemResultServerAddr())
        logger.debug(f"Original result server address: {result_server_addr}")

        if result_server_addr.startswith("127.0.0.1:"):
            # This is a localhost address that won't work from the farm
            port = result_server_addr.split(":")[1]
            local_ip = self.get_local_ip()
            result_server_addr = f"{local_ip}:{port}"
            logger.info(f"Replaced localhost with machine IP: {result_server_addr}")

        logger.info(f"PDG Result Server: {result_server_addr}")
        logger.warning(f"Make sure firewall allows incoming connections on port {result_server_addr.split(':')[1]}")

        job_env = {
            "PDG_RESULT_SERVER": result_server_addr,
            "PDG_DIR": str(self.context.workingDir(False)),
            "PDG_TEMP": str(self.context.tempDir(False)),
            "PDG_SCRIPTDIR": str(self.context.scriptDir(False)),
            "PDG_RENDER_DIR": render_dir,
            "PDG_RPC_TIMEOUT": "60",
            "PDG_RPC_MAX_ERRORS": "20",
            "PDG_RPC_BATCH": "1",
            "PDG_RPC_RETRY_DELAY": "5",
            "PDG_RPC_IGNORE_WORK_ITEM_RESULTS": "0",
            "PDG_SUBMIT_AS_JOB": "0",
            "PDG_WORK_ITEM_ID": str(work_item.id) if not should_batch else "1",
            "HOUDINI_TEMP_DIR": os.path.join(str(self.context.workingDir(False)), "render"),
        }

        # Get the multiple_machines parameter
        use_multiple_machines = rops.get_parameter_value(self.node, "multiple_machines")
        logger.debug(f"Use multiple machines: {use_multiple_machines}")

        # Apply threading configuration
        job_env = configure_threading_environment(self.node, use_multiple_machines, job_env)

        # For single task, add task-specific environment
        if not should_batch:
            job_env["PDG_ITEM_NAME"] = str(work_item.name)
            job_env["PDG_ITEM_ID"] = str(work_item.id)
            logger.debug("Added single task environment variables")

        # Include custom environment
        env_attr = work_item.stringAttribValue("conductor_environment")
        if env_attr:
            try:
                custom_env = json.loads(env_attr)
                job_env.update(custom_env)
                logger.debug(f"Added custom environment: {custom_env}")
            except json.JSONDecodeError:
                logger.warning("Failed to parse conductor_environment JSON")

        # Add conductor environment
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

        logger.debug("Final environment variables:")
        for key, value in job_env.items():
            logger.debug(f"  {key}: {value}")
        return job_env

    def submit_job_to_conductor(self, job_spec, work_item, work_item_chain, should_batch):
        """Submit the job to Conductor

        Args:
            job_spec: The job specification dictionary
            work_item: The current work item
            work_item_chain: List of work items in the batch
            should_batch: Whether this is a batch job

        Returns:
            pdg.scheduleResult: The scheduling result
        """
        logger.info("═════════════════════════════════════════════════════════")
        logger.info("JOB SPECIFICATION:")
        logger.info("═════════════════════════════════════════════════════════")
        logger.debug(f"{json.dumps(job_spec, indent=2)}")
        logger.info("═════════════════════════════════════════════════════════")

        logger.info("Submitting to Conductor...")
        submission_start = time.time()
        from ciocore import conductor_submit

        # Implement this
        use_submission_dialog = True

        if use_submission_dialog:
            def show_dialog():
                try:
                    nodes = [self.node]
                    payloads = [job_spec]
                    submission_dialog = SubmissionDialog(nodes, payloads=payloads)
                    submission_dialog.exec_()  # Use exec_() for modal dialog
                except Exception as e:
                    logger.error(f"Dialog error: {e}")

            # Execute on main thread - already imported hdefereval at top
            hdefereval.executeInMainThreadWithResult(show_dialog)
        else:
            try:
                remote_job = conductor_submit.Submit(job_spec)
                response, code = remote_job.main()
                submission_end = time.time()

                logger.info(f"Conductor response received in {submission_end - submission_start:.2f} seconds")
                logger.debug(f"Response code: {code}")
                logger.debug(f"Response: {json.dumps(response, indent=2)}")

                if code in (200, 201):
                    job_id = response.get("jobid")
                    if job_id:
                        work_item.setStringAttrib("conductor_job_id", job_id)
                        logger.debug("Set conductor_job_id attribute on work item")

                        # If batch job, update all items with the job ID
                        if should_batch:
                            logger.info(f"Updating all {len(work_item_chain)} batch items with job ID...")
                            for idx, item in enumerate(work_item_chain):
                                item.setStringAttrib("conductor_batch_job_id", job_id)
                                logger.debug(f"  Updated item {idx + 1}/{len(work_item_chain)}: {item.name}")

                        logger.info("╔═════════════════════════════════════════════════════════════╗")
                        logger.info("║                    JOB SUBMITTED SUCCESSFULLY               ║")
                        logger.info(f"║  Job ID: {job_id:<50}║")
                        logger.info("╚═════════════════════════════════════════════════════════════╝")

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

    def on_schedule(self, work_item):
        """Main scheduling function for work items

        Args:
            work_item: The work item to schedule

        Returns:
            pdg.scheduleResult: The scheduling result
        """
        logger.info("Custom onSchedule (Conductor version)")
        logger.debug(f"Script started at: {datetime.datetime.now()}")
        logger.debug(f"work_item: {work_item}")
        logger.debug(f"work_item type: {type(work_item)}")

        # Log the current work item in detail
        self.log_work_item_details(work_item, logging.DEBUG)

        # Log the PDG graph state
        self.log_pdg_graph_state(work_item, logging.DEBUG)

        try:
            # Ensure local staging
            logger.debug("Creating job directories and serializing work items...")
            self.context.createJobDirsAndSerializeWorkItems(work_item)
            logger.debug("Work item serialized successfully")

            # Expand the command that would have run locally - for logging purposes only
            local_command = self.context.expandCommandTokens(work_item.command, work_item)
            logger.debug(f"Local command (for reference): {local_command}")

            # Note: We're removing command parsing since the wrapper script will handle execution

            # Check if this work item has already been submitted as part of a batch
            batch_job_id = work_item.stringAttribValue("conductor_batch_job_id")
            logger.debug(f"Current batch_job_id: {batch_job_id}")

            if batch_job_id and batch_job_id != "pending":
                logger.info(f"Work item already submitted in batch job: {batch_job_id}")
                return pdg.scheduleResult.Succeeded

            # Connect to Conductor and ensure connection is valid
            try:
                connect_to_conductor(self.node)
            except RuntimeError as e:
                logger.error(f"Failed to establish Conductor connection: {e}")
                return pdg.scheduleResult.Failed
            except Exception as e:
                logger.error(f"Unexpected error connecting to Conductor: {e}")
                return pdg.scheduleResult.Failed

            # Define the render directory path
            render_dir = rops.get_parameter_value(self.node, "override_image_output")
            if not render_dir:
                render_dir = os.path.join(str(self.context.workingDir(False)), "pdg_render")
            logger.debug(f"Render directory: {render_dir}")
            logger.debug(f"Render directory exists: {os.path.exists(render_dir)}")

            # Collect all ready work items from the current node
            work_item_chain = []
            should_batch = False

            # Check if we're the first work item to be scheduled
            first_to_schedule = self.check_first_to_schedule(work_item)

            if first_to_schedule:
                # Collect all work items from this node that are ready to be scheduled
                work_item_chain = self.collect_work_items_for_batch(work_item)
                should_batch = len(work_item_chain) > 1
                logger.info(f"First to schedule, collecting all ready items. Found {len(work_item_chain)} items")
                logger.info(f"Should batch: {should_batch}")
            else:
                # Not first, check if already part of a batch
                if batch_job_id == "pending":
                    logger.debug("Work item is pending batch submission, skipping")
                    return pdg.scheduleResult.Succeeded
                # Otherwise submit as single task
                work_item_chain = [work_item]
                should_batch = False
                logger.info("Not first to schedule, submitting as single task")

            # Get the TOP network path
            topnet_path = self.get_topnet_path(work_item.node)
            logger.debug(f"TOP network path: {topnet_path}")

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
                logger.warning(
                    f"Wrapper script not found at {wrapper_script_source}. Falling back to default if available.")

            # Get the HIP filename for the job title
            hip_file_path = hou.hipFile.path()
            hip_filename = os.path.splitext(os.path.basename(hip_file_path))[0] if hip_file_path else "untitled"
            logger.debug(f"HIP filename: {hip_filename}")

            # Prepare job based on batch or single
            if should_batch:
                tasks_data, upload_paths, job_title = self.prepare_batch_job(
                    work_item_chain, topnet_path, wrapper_script_source
                )
            else:
                tasks_data, upload_paths, job_title = self.prepare_single_job(
                    work_item, topnet_path, wrapper_script_source
                )

            # Build job environment
            kwargs = {
                "do_asset_scan": True,
                "task_limit": -1
            }
            frame_range_to_use = self.node.parm("frame_range").evalAsString()
            job_env = self.build_job_environment(work_item, should_batch, render_dir)

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
                "output_path": render_dir,
                "local_upload": True,
                "scout_frames": scout_frames,
                "tasks_data": tasks_data,
                "upload_paths": upload_paths,
            }


            # Submit job to Conductor
            return self.submit_job_to_conductor(job_spec, work_item, work_item_chain, should_batch)

        except Exception as e:
            logger.error("═════════════════════════════════════════════════════════")
            logger.error("CRITICAL ERROR IN onSchedule")
            logger.error("═════════════════════════════════════════════════════════")
            logger.error(traceback.format_exc())
            logger.error("═════════════════════════════════════════════════════════")
            return pdg.scheduleResult.Failed


# Entry point function to be called from the scheduler
def schedule_work_item(scheduler_self, work_item):
    """Entry point function for scheduling work items

    Args:
        scheduler_self: The scheduler context (self from PDG)
        work_item: The work item to schedule

    Returns:
        pdg.scheduleResult: The scheduling result
    """
    # from ciohoudini.scheduler.on_schedule_conductor_scheduler import PDGConductorScheduler
    # import hou

    scheduler_name = self.name
    logger.debug(f"scheduler_name: {scheduler_name}")

    # Find the topnet node by traversing up the parent hierarchy
    current_node = work_item.node.topNode()
    topnet_hou_node = None

    # Keep going up until we find a topnet node or reach the root
    while current_node is not None:
        if current_node.type().name() == "topnet":
            topnet_hou_node = current_node
            break
        current_node = current_node.parent()

    if topnet_hou_node is None:
        logger.error("Could not find topnet node in parent hierarchy")
        result = pdg.scheduleResult.Failed
    else:
        logger.debug(f"topnet_hou_node: {topnet_hou_node.name()}")
        logger.debug(f"topnet_hou_node path: {topnet_hou_node.path()}")

        # Find our specific conductor scheduler by name
        scheduler_node = None
        for node in topnet_hou_node.allSubChildren():
            if (node.type().name() == "conductorscheduler" and
                    node.name() == scheduler_name):
                scheduler_node = node
                node_path = scheduler_node.path()
                break

        if scheduler_node:
            logger.debug(f"scheduler_node: {scheduler_node.path()}")
            logger.debug(f"node_path: {node_path}")
            scheduler = PDGConductorScheduler(self, node_path=node_path)
            result = scheduler.on_schedule(work_item)
        else:
            logger.error(f"Could not find conductorscheduler named '{scheduler_name}' in {topnet_hou_node.path()}")
            result = pdg.scheduleResult.Failed

    return result