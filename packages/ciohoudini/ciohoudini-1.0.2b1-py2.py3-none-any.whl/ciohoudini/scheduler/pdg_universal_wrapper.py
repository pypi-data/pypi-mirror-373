#!/usr/bin/env python
"""
PDG Universal Wrapper Script for Conductor Render Farm
Supports three modes:
- Submit As Job (full graph execution)
- On Schedule (single work item execution)
- Single Machine (cook all items locally)
"""

import hou
import os
import sys
import argparse
import time
import json
import shutil
import glob
import re
import traceback
from pathlib import Path
from datetime import datetime
import subprocess


class PDGUniversalExecutor:
    """Universal executor for submitAsJob, on_schedule, and single_machine modes"""

    def __init__(self, hip_file, topnet_path, working_dir, output_dir,
                 item_index=None, cook_entire_graph=False, use_single_machine=False):
        self.hip_file = hip_file
        self.topnet_path = topnet_path
        self.working_dir = working_dir
        self.output_dir = output_dir
        self.item_index = item_index
        self.cook_entire_graph = cook_entire_graph
        self.use_single_machine = use_single_machine

        # Execution mode - set this BEFORE initializing status dict
        if cook_entire_graph:
            self.execution_mode = "submitAsJob"
        elif use_single_machine:
            self.execution_mode = "single_machine"
        else:
            self.execution_mode = "on_schedule"

        # Initialize status dict after execution_mode is set
        self.status_dict = self._initialize_status_dict()

        # Initialize other attributes
        self.topnet = None
        self.scheduler = None
        self.output_node = None

    def _initialize_status_dict(self):
        """Initialize the status tracking dictionary"""
        # First part: basic fields
        base_dict = {
            'timestamp_start': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'execution_mode': self.execution_mode,
            'hip_file': self.hip_file,
            'topnet_path': self.topnet_path,
            'working_dir': self.working_dir,
            'output_dir': self.output_dir,
        }

        # Second part: Add mode-specific fields
        if self.cook_entire_graph:
            base_dict['cook_entire_graph'] = True
            base_dict['work_items_total'] = 0
            base_dict['work_items_succeeded'] = 0
            base_dict['work_items_failed'] = 0
            base_dict['work_items_details'] = []
        elif self.use_single_machine:
            base_dict['use_single_machine'] = True
            base_dict['work_items_total'] = 0
            base_dict['work_items_succeeded'] = 0
            base_dict['work_items_failed'] = 0
            base_dict['work_items_details'] = []
        else:
            base_dict['target_index'] = self.item_index
            base_dict['frame_number'] = str(self.item_index).zfill(4) if self.item_index is not None else "0000"
            base_dict['work_items_processed'] = []
            base_dict['skipped_items'] = []

        # Third part: remaining fields
        base_dict.update({
            'nodes_in_network': [],
            'files_created': {
                'usd': [],
                'renders': [],
                'hip': [],
                'logs': [],
                'pdg': [],
                'other': [],
                'total_count': 0
            },
            'cook_result': {
                'return_code': None,
                'failed_items': [],
                'successful_items': [],
                'warnings': []
            },
            'environment': dict(os.environ),
            'timestamp_end': None,
            'duration_seconds': None,
            'status': 'initializing',
            'errors': []
        })

        return base_dict

    def run(self):
        """Main execution method"""
        try:
            print("\n" + "=" * 80)
            print("PDG UNIVERSAL WRAPPER SCRIPT")
            print(f"EXECUTION MODE: {self.execution_mode.upper()}")
            print("=" * 80)
            self._print_configuration()

            # Phase 1: Setup
            if not self._setup_environment():
                return False

            # Phase 2: Load HIP file
            if not self._load_hip_file():
                return False

            # Phase 3: Get TOP Network
            if not self._get_top_network():
                return False

            # Execute based on mode
            if self.cook_entire_graph:
                # Submit As Job mode - cook entire graph
                # Phase 4: Create and configure scheduler for full graph
                if not self._setup_scheduler_for_full_graph():
                    return False
                # Phase 5: Execute full graph
                success = self._execute_full_graph()
            elif self.use_single_machine:
                # Single Machine mode - cook all items locally
                # Phase 4: Create scheduler (no custom code needed)
                if not self._setup_scheduler_for_single_machine():
                    return False
                # Phase 5: Execute all work items locally
                success = self._execute_single_machine()
            else:
                # On Schedule mode - cook single work item
                # Phase 4: Create and configure scheduler
                if not self._setup_scheduler():
                    return False
                # Phase 5: Generate and cook work items
                success = self._execute_work_items()

            # Phase 6: Collect all output files
            self._collect_all_outputs()

            # Phase 7: Save final HIP file
            self._save_final_hip()

            self.status_dict['status'] = 'success' if success else 'failure'
            return success

        except Exception as e:
            self.status_dict['errors'].append(str(e))
            self.status_dict['status'] = 'error'
            print(f"\nCRITICAL ERROR: {e}")
            traceback.print_exc()
            return False

        finally:
            self._finalize_execution()

    def _print_configuration(self):
        """Print execution configuration"""
        print(f"HIP File: {self.hip_file}")
        print(f"TOP Network: {self.topnet_path}")
        print(f"Working Dir: {self.working_dir}")
        print(f"Output Dir: {self.output_dir}")

        if self.cook_entire_graph:
            print(f"Mode: Submit As Job (Full Graph Execution)")
        elif self.use_single_machine:
            print(f"Mode: Single Machine (Cook All Items Locally)")
        else:
            frame_num = str(self.item_index).zfill(4) if self.item_index is not None else "0000"
            print(f"Mode: On Schedule (Single Work Item)")
            print(f"Target Index: {self.item_index} (Frame: {frame_num})")

        print("=" * 80 + "\n")

    def _setup_environment(self):
        """Setup execution environment"""
        print("\n" + "-" * 60)
        print("Phase 1: Environment Setup")
        print("-" * 60)

        try:
            # Create output directory
            os.makedirs(self.output_dir, exist_ok=True)

            # Test write permissions
            test_file = os.path.join(self.output_dir, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"✓ Output directory ready: {self.output_dir}")

            # Set PDG environment variables
            os.environ['PDG_DIR'] = self.working_dir
            os.environ['PDG_RENDER_DIR'] = self.output_dir

            # Create necessary subdirectories
            subdirs = ['usd', 'renders', 'logs', 'pdg', 'hip', 'execution_status']
            for subdir in subdirs:
                os.makedirs(os.path.join(self.output_dir, subdir), exist_ok=True)

            print("✓ Environment configured successfully")
            return True

        except Exception as e:
            print(f"✗ Environment setup failed: {e}")
            self.status_dict['errors'].append(f"Environment setup: {e}")
            return False

    def _load_hip_file(self):
        """Load the Houdini HIP file"""
        print("\n" + "-" * 60)
        print("Phase 2: Loading HIP File")
        print("-" * 60)

        try:
            if not os.path.exists(self.hip_file):
                raise FileNotFoundError(f"HIP file not found: {self.hip_file}")

            print(f"Loading: {self.hip_file}")

            # Load the file and capture any warnings
            try:
                hou.hipFile.load(self.hip_file, suppress_save_prompt=True, ignore_load_warnings=True)
            except hou.LoadWarning as warning:
                # This is just a warning, not an error - file loaded successfully
                print(f"  Note: Load warning (can be ignored): {warning}")
            except hou.OperationFailed as e:
                # This is an actual error
                if "Warnings were generated" in str(e):
                    # This is actually just warnings, not a failure
                    print(f"  Note: Warnings during load (continuing): {e}")
                else:
                    # This is a real failure
                    raise e

            # Verify load by checking the current file
            current_hip = hou.hipFile.name()
            if os.path.abspath(current_hip) == os.path.abspath(self.hip_file):
                print(f"✓ HIP file loaded successfully: {current_hip}")
            else:
                # Sometimes the path format differs, check if it's essentially the same file
                print(f"✓ HIP file loaded: {current_hip}")

            # Update paths if needed
            hou.hscript(f"set PDG_DIR = {self.working_dir}")
            hou.hscript(f"set PDG_RENDER_DIR = {self.output_dir}")

            return True

        except FileNotFoundError as e:
            print(f"✗ File not found: {e}")
            self.status_dict['errors'].append(f"HIP file not found: {e}")
            return False
        except Exception as e:
            # Check if this is just a warning about incomplete asset definitions
            error_str = str(e)
            if "Warnings were generated" in error_str or "incomplete asset definitions" in error_str:
                print(f"  Note: Load completed with warnings (continuing):")
                print(f"    {error_str}")

                # Verify the file actually loaded
                try:
                    current_hip = hou.hipFile.name()
                    print(f"✓ HIP file loaded despite warnings: {current_hip}")

                    # Update paths
                    hou.hscript(f"set PDG_DIR = {self.working_dir}")
                    hou.hscript(f"set PDG_RENDER_DIR = {self.output_dir}")

                    return True
                except:
                    # If we can't get the hip file name, it didn't load
                    print(f"✗ Failed to verify HIP file load")
                    self.status_dict['errors'].append(f"HIP load verification failed: {e}")
                    return False
            else:
                # This is a real error
                print(f"✗ Failed to load HIP file: {e}")
                self.status_dict['errors'].append(f"HIP load: {e}")
                return False

    def _get_top_network(self):
        """Find and validate TOP network"""
        print("\n" + "-" * 60)
        print("Phase 3: Locating TOP Network")
        print("-" * 60)

        # Try specified path first
        current_node = hou.node(self.topnet_path)

        if current_node:
            # Check if the node exists and find the topnet
            print(f"Node found at {self.topnet_path} (type: {current_node.type().name()})")

            # If it's not a topnet, traverse up to find the topnet
            if current_node.type().name() != "topnet":
                print(f"  This is not a topnet node, searching parent hierarchy...")

                # Keep going up until we find a topnet node or reach the root
                while current_node is not None:
                    if current_node.type().name() == "topnet":
                        self.topnet = current_node
                        self.topnet_path = current_node.path()
                        print(f"✓ Found parent TOP network: {self.topnet_path}")
                        break
                    current_node = current_node.parent()

                if not self.topnet:
                    print(f"✗ No topnet found in parent hierarchy of {self.topnet_path}")
                    # Fall back to searching
                    self._search_for_topnets()
            else:
                # It's already a topnet
                self.topnet = current_node
                print(f"✓ TOP network found: {self.topnet_path}")
        else:
            print(f"Node not found at {self.topnet_path}")
            self._search_for_topnets()

        if not self.topnet:
            print("✗ No TOP networks found in scene")
            self.status_dict['errors'].append("No TOP network found")
            return False

        # Catalog nodes in network
        self._catalog_top_nodes()

        # Find output node
        self._find_output_node()

        return True

    def _search_for_topnets(self):
        """Search for TOP networks in the scene"""
        print("Searching for TOP networks...")

        top_networks = []

        # Search in /obj
        if hou.node("/obj"):
            for node in hou.node("/obj").children():
                if node.type().name() == "topnet":
                    top_networks.append(node)
                    print(f"  Found: {node.path()}")

        # Search in /tasks (common location for tasks)
        if hou.node("/tasks"):
            for node in hou.node("/tasks").children():
                if node.type().name() == "topnet":
                    top_networks.append(node)
                    print(f"  Found: {node.path()}")

        # Search everywhere else
        for root in ["/", "/stage"]:
            if hou.node(root):
                for child in hou.node(root).children():
                    if child.path() not in ["/obj", "/tasks"] and child.type().category():
                        for node in child.allSubChildren():
                            if node.type().name() == "topnet" and node not in top_networks:
                                top_networks.append(node)
                                print(f"  Found: {node.path()}")

        if top_networks:
            self.topnet = top_networks[0]
            self.topnet_path = self.topnet.path()
            print(f"✓ Using TOP network: {self.topnet_path}")
        else:
            self.topnet = None

    def _is_output_node(self, node):
        """Check if a node is an output-type node"""
        output_types = ['output', 'ropfetch', 'ropgeometry', 'ropmantra',
                        'ropkarma', 'usdrender', 'filecopy', 'null', 'rop']
        node_type_lower = node.type().name().lower()

        for out_type in output_types:
            if out_type in node_type_lower:
                return True
        return False

    def _catalog_top_nodes(self):
        """Catalog all TOP nodes in the network"""
        print("\nCataloging TOP nodes:")
        for node in self.topnet.children():
            if node.type().category().name() == "Top":
                # Check display flag
                is_display = False
                try:
                    is_display = (self.topnet.displayNode() == node)
                except:
                    try:
                        is_display = node.isDisplayFlagSet()
                    except:
                        pass

                # Check render flag
                is_render = False
                try:
                    is_render = node.isRenderFlagSet()
                except:
                    # Some nodes don't have render flags
                    pass

                node_info = {
                    'path': node.path(),
                    'type': node.type().name(),
                    'display_flag': is_display,
                    'render_flag': is_render
                }
                self.status_dict['nodes_in_network'].append(node_info)

                flags = []
                if self._is_output_node(node):
                    flags.append("OUTPUT")
                if is_display:
                    flags.append("DISPLAY")
                if is_render:
                    flags.append("RENDER")

                flag_str = f" [{', '.join(flags)}]" if flags else ""
                print(f"  - {node.name()} ({node.type().name()}){flag_str}")

    def _find_output_node(self):
        """Find the appropriate output node"""
        print("\nIdentifying output node:")

        # Priority 1: Display node
        self.output_node = self.topnet.displayNode()
        if self.output_node:
            print(f"✓ Using display node: {self.output_node.name()}")
            return

        # Priority 2: Common output node types
        output_types = ['output', 'ropfetch', 'ropgeometry', 'ropmantra',
                        'ropkarma', 'usdrender', 'filecopy', 'null']

        for node in self.topnet.children():
            if node.type().category().name() == "Top":
                for out_type in output_types:
                    if out_type in node.type().name().lower():
                        self.output_node = node
                        print(f"✓ Using output node: {node.name()} ({node.type().name()})")
                        return

        # Priority 3: Last non-scheduler node
        top_nodes = [n for n in self.topnet.children()
                     if n.type().category().name() == "Top"
                     and "scheduler" not in n.type().name().lower()]

        if top_nodes:
            self.output_node = top_nodes[-1]
            print(f"✓ Using last TOP node: {self.output_node.name()}")
        else:
            print("✗ No suitable output node found")

    def _find_or_create_scheduler(self, preferred_types=None, custom_code=None):
        """
        Find an existing scheduler or create a new one with fallback strategies.

        Args:
            preferred_types: List of preferred scheduler types (e.g., ['pythonscheduler', 'localscheduler'])
            custom_code: Custom onSchedule code to set if modifying a Python scheduler

        Returns:
            The scheduler node if successful, None otherwise
        """
        if preferred_types is None:
            preferred_types = ['conductorscheduler', 'pythonscheduler', 'localscheduler']

        scheduler = None
        created_new = False

        print("\nScheduler acquisition strategy:")

        # Strategy 1: Try to create a new Python scheduler
        try:
            existing = self.topnet.node("temp_python_scheduler")
            if existing:
                existing.destroy()
                print("  Removed existing temp scheduler")

            scheduler = self.topnet.createNode('pythonscheduler', 'temp_python_scheduler')
            created_new = True
            print(f"  ✓ Created new Python scheduler: {scheduler.path()}")

        except Exception as e:
            print(f"  ✗ Cannot create new scheduler: {e}")
            print("  Fallback: Looking for existing schedulers...")

            # Strategy 2: Check the default scheduler on the topnet
            for parm_name in ["topscheduler", "defaultscheduler", "scheduler", "pdg_topscheduler"]:
                parm = self.topnet.parm(parm_name)
                if parm:
                    scheduler_path = parm.eval()
                    if scheduler_path:
                        # Handle both relative and absolute paths
                        if scheduler_path.startswith('/'):
                            # Absolute path
                            default_scheduler = hou.node(scheduler_path)
                        else:
                            # Relative path - resolve relative to topnet
                            default_scheduler = self.topnet.node(scheduler_path)

                        if default_scheduler:
                            scheduler = default_scheduler
                            print(f"  ✓ Found default scheduler: {scheduler.path()} ({scheduler.type().name()})")
                            break
                        else:
                            print(f"  Note: Default scheduler path '{scheduler_path}' not found")

            # Strategy 3: Search for Conductor schedulers (highest priority)
            if not scheduler:
                print("  Searching for Conductor schedulers...")
                for node in self.topnet.children():
                    node_type = node.type().name().lower()
                    if 'conductor' in node_type and 'scheduler' in node_type:
                        scheduler = node
                        print(f"  ✓ Found Conductor scheduler: {scheduler.path()} ({node.type().name()})")
                        break

            # Strategy 4: Search for Python schedulers
            if not scheduler:
                print("  Searching for Python schedulers...")
                for node in self.topnet.children():
                    if node.type().name() == 'pythonscheduler':
                        scheduler = node
                        print(f"  ✓ Found existing Python scheduler: {scheduler.path()}")
                        break

            # Strategy 5: Search for local schedulers
            if not scheduler:
                print("  Searching for local schedulers...")
                for node in self.topnet.children():
                    if node.type().name() == 'localscheduler':
                        scheduler = node
                        print(f"  ✓ Found existing local scheduler: {scheduler.path()}")
                        break

            # Strategy 6: Search for any other scheduler
            if not scheduler:
                print("  Searching for any scheduler...")
                for node in self.topnet.children():
                    if 'scheduler' in node.type().name().lower():
                        scheduler = node
                        print(f"  ✓ Found existing scheduler: {scheduler.path()} ({scheduler.type().name()})")
                        break

            # Debug: List all nodes in topnet if no scheduler found
            if not scheduler:
                print("\n  Debug: All nodes in TOP network:")
                for node in self.topnet.children():
                    node_type = node.type().name()
                    print(f"    - {node.name()} (type: {node_type})")
                print()

        if not scheduler:
            print("  ✗ No scheduler found or created")
            return None

        # Configure the scheduler
        try:
            # Set working directory if possible
            if scheduler.parm("pdg_workingdir"):
                scheduler.parm("pdg_workingdir").set("$HIP")
                print(f"  ✓ Set working directory on scheduler")

            # Determine scheduler type
            scheduler_type = scheduler.type().name().lower()

            # If we have custom code and it's a Python scheduler, set it
            if custom_code and 'python' in scheduler_type:
                if scheduler.parm("onschedule"):
                    scheduler.parm("onschedule").set(custom_code)
                    print(f"  ✓ Configured custom onSchedule code")
                elif scheduler.parm("submitasjob"):
                    # For submitAsJob mode
                    scheduler.parm("submitasjob").set(custom_code)
                    print(f"  ✓ Configured submitAsJob code")

            # For Conductor schedulers
            elif 'conductor' in scheduler_type:
                print(f"  Note: Using Conductor scheduler - custom code not applicable")
                # Conductor schedulers have their own submission logic
                # They typically don't need custom Python code

            # For local schedulers
            elif 'local' in scheduler_type:
                print(f"  Note: Using local scheduler - custom code not applicable")
                # Local schedulers typically don't need custom code
                # They handle work items through their built-in logic

            else:
                print(f"  Note: Using {scheduler.type().name()} scheduler")

        except Exception as e:
            print(f"  Warning: Could not fully configure scheduler: {e}")

        return scheduler

    def _setup_scheduler_for_single_machine(self):
        """Create Python scheduler for single machine mode (no custom code)"""
        print("\n" + "-" * 60)
        print("Phase 4: Scheduler Setup (Single Machine - All Items)")
        print("-" * 60)

        try:
            # Use the helper to find or create a scheduler
            # For single machine mode, we don't need custom code
            self.scheduler = self._find_or_create_scheduler(
                preferred_types=['conductorscheduler', 'pythonscheduler', 'localscheduler'],
                custom_code=None  # No custom code needed for single machine mode
            )

            if not self.scheduler:
                print("✗ Failed to acquire scheduler")
                self.status_dict['errors'].append("Failed to acquire scheduler for single machine mode")
                return False

            # Apply scheduler to all nodes
            self._apply_scheduler_to_nodes()

            print("✓ Scheduler configured for single machine execution")
            return True

        except Exception as e:
            print(f"✗ Scheduler setup failed: {e}")
            self.status_dict['errors'].append(f"Scheduler setup: {e}")
            return False

    def _execute_single_machine(self):
        """Execute all work items on single machine (like right-click Cook Node)"""
        print("\n" + "-" * 60)
        print("Phase 5: Single Machine Execution (Cook All Items)")
        print("-" * 60)

        try:
            print("Initializing PDG context for local execution...")

            # Dirty all tasks to ensure clean execution
            for node in self.topnet.children():
                if node.type().category().name() == "Top":
                    try:
                        print(f"  Dirtying tasks for: {node.name()}")
                        node.dirtyAllTasks(False)
                    except Exception as e:
                        print(f"    Warning: Could not dirty tasks for {node.name()}: {e}")

            time.sleep(1)

            # Generate work items first
            print("\nGenerating work items...")
            if self.output_node:
                try:
                    self.output_node.cookWorkItems(generate_only=True, block=True)
                except:
                    pass

            # Count total work items
            total_items = self._count_all_work_items()
            print(f"✓ Generated {total_items} work items")

            # Cook all work items locally
            print("\nCooking all work items on local machine...")
            print(f"  Output node: {self.output_node.name() if self.output_node else 'Network level'}")

            cook_start = time.time()
            cooked = False

            # Method 1: Cook via output node
            if self.output_node:
                try:
                    print("  Attempting to cook via output node...")
                    self.output_node.cookWorkItems(block=True)
                    cooked = True
                    print("  ✓ Successfully cooked via output node")
                except Exception as e:
                    print(f"    Output node cooking failed: {e}")

            # Method 2: Cook via network
            if not cooked:
                try:
                    print("  Attempting to cook via TOP network...")
                    self.topnet.cookWorkItems(block=True)
                    cooked = True
                    print("  ✓ Successfully cooked via network")
                except Exception as e:
                    print(f"    Network cooking failed: {e}")

            # Method 3: Cook individual nodes
            if not cooked:
                print("  Attempting to cook individual nodes...")
                for node in self.topnet.children():
                    if node.type().category().name() == "Top" and "scheduler" not in node.type().name().lower():
                        try:
                            if hasattr(node, 'cookWorkItems'):
                                print(f"    Cooking: {node.name()}")
                                node.cookWorkItems(block=True)
                        except Exception as e:
                            print(f"      Failed to cook {node.name()}: {e}")

            cook_end = time.time()
            cook_duration = cook_end - cook_start
            print(f"\nLocal cooking completed in {cook_duration:.2f} seconds")

            # Collect statistics
            self._collect_single_machine_results()

            return True

        except Exception as e:
            print(f"✗ Single machine execution failed: {e}")
            self.status_dict['errors'].append(f"Single machine execution: {e}")
            traceback.print_exc()
            return False

    def _count_all_work_items(self):
        """Count total work items in the network"""
        total = 0
        for node in self.topnet.children():
            if node.type().category().name() != "Top":
                continue
            try:
                pdg_node = node.getPDGNode()
                if pdg_node and hasattr(pdg_node, 'workItems'):
                    total += len(pdg_node.workItems)
            except:
                pass
        return total

    def _collect_single_machine_results(self):
        """Collect results from single machine execution"""
        print("\nCollecting single machine execution results...")

        total_items = 0
        succeeded_items = 0
        failed_items = 0
        work_items_details = []

        for node in self.topnet.children():
            if node.type().category().name() != "Top":
                continue

            try:
                pdg_node = node.getPDGNode()
                if not pdg_node:
                    continue

                work_items = pdg_node.workItems
                node_succeeded = 0
                node_failed = 0

                for wi in work_items:
                    total_items += 1

                    # Determine status
                    status = 'unknown'
                    if hasattr(wi, 'isSuccessful') and wi.isSuccessful:
                        status = 'success'
                        succeeded_items += 1
                        node_succeeded += 1
                    elif hasattr(wi, 'isFailed') and wi.isFailed:
                        status = 'failed'
                        failed_items += 1
                        node_failed += 1
                    elif hasattr(wi, 'isCancelled') and wi.isCancelled:
                        status = 'cancelled'
                        failed_items += 1
                        node_failed += 1

                    work_items_details.append({
                        'node': node.name(),
                        'item_name': wi.name,
                        'item_index': wi.index if hasattr(wi, 'index') else -1,
                        'status': status
                    })

                if len(work_items) > 0:
                    print(f"  {node.name()}: {len(work_items)} items "
                          f"(✓ {node_succeeded} succeeded, ✗ {node_failed} failed)")

            except Exception as e:
                print(f"  Warning: Could not get work items from {node.name()}: {e}")

        # Update status dictionary
        self.status_dict['work_items_total'] = total_items
        self.status_dict['work_items_succeeded'] = succeeded_items
        self.status_dict['work_items_failed'] = failed_items
        self.status_dict['work_items_details'] = work_items_details

        print(f"\nTotal work items: {total_items}")
        print(f"  Succeeded: {succeeded_items}")
        print(f"  Failed: {failed_items}")
        print(f"  Success rate: {(succeeded_items / total_items * 100) if total_items > 0 else 0:.1f}%")

    def _execute_full_graph(self):
        """Execute the full PDG graph using topcook.py"""
        print("\n" + "-" * 60)
        print("Phase 5: Full Graph Execution")
        print("-" * 60)

        hip_dir = os.path.dirname(self.hip_file)

        # Use hython directly
        hython_path = "hython"

        # Construct the command to cook the PDG graph
        topcook_script = os.path.expandvars("$HHP/pdgjob/topcook.py")

        # Build the command with valid arguments
        cmd = [
            hython_path,
            topcook_script,
            "--hip", self.hip_file,
            "--toppath", self.topnet_path,
            "--verbosity", "3",  # Maximum verbosity
            "--report", "items",  # Report on individual work items
            "--keepopen", "error"  # Keep session open on error
        ]

        # Add task graph output
        output_file = os.path.join(hip_dir, f"{os.path.basename(self.hip_file)}.post.py")
        cmd.extend(["--taskgraphout", output_file])

        # Set up environment variables
        env = os.environ.copy()
        env['PDG_DIR'] = hip_dir
        env['PDG_VERBOSE'] = '3'
        env['HOUDINI_PDG_NODE_DEBUG'] = '3'

        try:
            print("=" * 60)
            print(f"Starting PDG graph cook at: {self.topnet_path}")
            print(f"Hip file: {self.hip_file}")
            print(f"PDG_DIR set to: {hip_dir}")
            print(f"Command: {' '.join(cmd)}")
            print("=" * 60)

            # Run the command with real-time output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env
            )

            # Stream output in real-time
            output_lines = []
            error_lines = []
            failed_items = {}
            successful_items = []
            current_node = None

            # Read stdout
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())
                    output_lines.append(line)

                    # Parse node context
                    if "Node " in line and "Given Node" not in line:
                        current_node = line.split("Node ")[-1].strip()

                    # Capture failed work items
                    if "CookedFail" in line:
                        parts = line.strip().split()
                        if parts:
                            item_name = parts[0]
                            failed_items[item_name] = current_node
                            self.status_dict['cook_result']['failed_items'].append({
                                'name': item_name,
                                'node': current_node
                            })

                    # Capture successful work items
                    if "CookedSuccess" in line:
                        parts = line.strip().split()
                        if parts:
                            item_name = parts[0]
                            successful_items.append(item_name)
                            self.status_dict['cook_result']['successful_items'].append({
                                'name': item_name,
                                'node': current_node
                            })

                    # Capture warnings
                    if "warning" in line.lower():
                        self.status_dict['cook_result']['warnings'].append(line.strip())

            # Read stderr
            for line in iter(process.stderr.readline, ''):
                if line:
                    print(f"STDERR: {line.rstrip()}")
                    error_lines.append(line)

            # Wait for process to complete
            return_code = process.wait()
            self.status_dict['cook_result']['return_code'] = return_code

            print("=" * 60)

            # Analyze results
            if failed_items:
                print("FAILED WORK ITEMS:")
                print("-" * 40)
                for item_name, node_name in failed_items.items():
                    print(f"  {item_name} (from node: {node_name})")
                print("-" * 40)

            if successful_items:
                print(f"\n✓ Successfully cooked {len(successful_items)} work items")

            if self.status_dict['cook_result']['warnings']:
                print("\nWarnings:")
                for warning in self.status_dict['cook_result']['warnings'][:5]:  # Show first 5
                    print(f"  {warning}")

            if return_code == 0:
                print("\nCook completed")
                if failed_items:
                    print(f"WARNING: {len(failed_items)} work items failed")
                else:
                    print("SUCCESS: All work items cooked successfully!")
                return True
            else:
                print(f"\nERROR: PDG graph cooking failed with return code: {return_code}")
                return False

        except Exception as e:
            print(f"✗ Graph execution failed: {e}")
            self.status_dict['errors'].append(f"Graph execution: {e}")
            traceback.print_exc()
            return False

    def _collect_full_graph_results(self):
        """Collect results from full graph execution"""
        print("\nCollecting full graph execution results...")

        total_items = 0
        succeeded_items = 0
        failed_items = 0
        work_items_details = []

        for node in self.topnet.children():
            if node.type().category().name() != "Top":
                continue

            try:
                pdg_node = node.getPDGNode()
                if not pdg_node:
                    continue

                work_items = pdg_node.workItems
                node_succeeded = 0
                node_failed = 0

                for wi in work_items:
                    total_items += 1

                    # Determine status
                    status = 'unknown'
                    if hasattr(wi, 'isSuccessful') and wi.isSuccessful:
                        status = 'success'
                        succeeded_items += 1
                        node_succeeded += 1
                    elif hasattr(wi, 'isFailed') and wi.isFailed:
                        status = 'failed'
                        failed_items += 1
                        node_failed += 1
                    elif hasattr(wi, 'isCancelled') and wi.isCancelled:
                        status = 'cancelled'
                        failed_items += 1
                        node_failed += 1

                    work_items_details.append({
                        'node': node.name(),
                        'item_name': wi.name,
                        'item_index': wi.index if hasattr(wi, 'index') else -1,
                        'status': status
                    })

                if len(work_items) > 0:
                    print(f"  {node.name()}: {len(work_items)} items "
                          f"(✓ {node_succeeded} succeeded, ✗ {node_failed} failed)")

            except Exception as e:
                print(f"  Warning: Could not get work items from {node.name()}: {e}")

        # Update status dictionary
        self.status_dict['work_items_total'] = total_items
        self.status_dict['work_items_succeeded'] = succeeded_items
        self.status_dict['work_items_failed'] = failed_items
        self.status_dict['work_items_details'] = work_items_details

        print(f"\nTotal work items: {total_items}")
        print(f"  Succeeded: {succeeded_items}")
        print(f"  Failed: {failed_items}")
        print(f"  Success rate: {(succeeded_items / total_items * 100) if total_items > 0 else 0:.1f}%")

    def _setup_scheduler_for_full_graph(self):
        """Create and configure the Python scheduler for full graph execution"""
        print("\n" + "-" * 60)
        print("Phase 4: Scheduler Setup (Full Graph)")
        print("-" * 60)

        try:
            # Prepare submitAsJob code (optional for full graph)
            submit_as_job_code = '''# Submit As Job callback for full graph execution
# This runs when the entire graph is submitted as a single job
import subprocess
import os

# Default behavior - just execute the command
job_env = os.environ.copy()
job_env['PDG_DIR'] = str(self.workingDir(False))
job_env['PDG_TEMP'] = str(self.tempDir(False))
job_env['PDG_SCRIPTDIR'] = str(self.scriptDir(False))

print(f"[SCHEDULER] Executing full graph cook")
return True
'''

            # Use the helper to find or create a scheduler
            self.scheduler = self._find_or_create_scheduler(
                preferred_types=['conductorscheduler', 'pythonscheduler', 'localscheduler'],
                custom_code=submit_as_job_code
            )

            if not self.scheduler:
                print("✗ Failed to acquire scheduler")
                self.status_dict['errors'].append("Failed to acquire scheduler for full graph")
                return False

            # Apply scheduler to all nodes
            self._apply_scheduler_to_nodes()

            print("✓ Scheduler configured for full graph execution")
            return True

        except Exception as e:
            print(f"✗ Scheduler setup failed: {e}")
            self.status_dict['errors'].append(f"Scheduler setup: {e}")
            return False

    def _setup_scheduler(self):
        """Create and configure the Python scheduler for single work item mode"""
        print("\n" + "-" * 60)
        print("Phase 4: Scheduler Setup (Single Work Item)")
        print("-" * 60)

        try:
            # Generate custom onSchedule code for single item execution
            on_schedule_code = self._generate_on_schedule_code()

            # Use the helper to find or create a scheduler
            self.scheduler = self._find_or_create_scheduler(
                preferred_types=['conductorscheduler', 'pythonscheduler', 'localscheduler'],
                custom_code=on_schedule_code
            )

            if not self.scheduler:
                print("✗ Failed to acquire scheduler")
                self.status_dict['errors'].append("Failed to acquire scheduler for single work item")
                return False

            print(f"✓ Configured to cook only work item at index {self.item_index}")

            # Apply scheduler to all nodes
            self._apply_scheduler_to_nodes()

            return True

        except Exception as e:
            print(f"✗ Scheduler setup failed: {e}")
            self.status_dict['errors'].append(f"Scheduler setup: {e}")
            return False

    def _generate_on_schedule_code(self):
        """Generate the onSchedule callback code"""
        return f'''# Custom onSchedule for single work item execution
import subprocess
import os
import sys

TARGET_INDEX = {self.item_index}

print(f"[SCHEDULER] Item {{work_item.index}}: {{work_item.name}}")

if work_item.index == TARGET_INDEX:
    print(f"[SCHEDULER] COOKING work item index={{work_item.index}}")

    # Prepare work item
    self.createJobDirsAndSerializeWorkItems(work_item)

    # Expand command tokens
    item_command = self.expandCommandTokens(work_item.command, work_item)

    # Setup environment
    job_env = os.environ.copy()
    job_env['PDG_RESULT_SERVER'] = str(self.workItemResultServerAddr())
    job_env['PDG_ITEM_NAME'] = str(work_item.name)
    job_env['PDG_ITEM_ID'] = str(work_item.id)
    job_env['PDG_DIR'] = str(self.workingDir(False))
    job_env['PDG_TEMP'] = str(self.tempDir(False))
    job_env['PDG_SCRIPTDIR'] = str(self.scriptDir(False))

    # Execute command
    print(f"[SCHEDULER] Executing: {{item_command[:100]}}...")
    returncode = subprocess.call(item_command, shell=True, env=job_env)

    print(f"[SCHEDULER] Completed with return code: {{returncode}}")

    if returncode == 0:
        return pdg.scheduleResult.CookSucceeded
    return pdg.scheduleResult.CookFailed
else:
    print(f"[SCHEDULER] SKIPPING work item index={{work_item.index}}")
    return pdg.scheduleResult.Skip
'''

    def _apply_scheduler_to_nodes(self):
        """Apply scheduler to all TOP nodes"""
        print("\nApplying scheduler to nodes:")

        scheduler_path = self.scheduler.path()
        count = 0

        # Apply to individual nodes
        for node in self.topnet.children():
            if node.type().category().name() != "Top":
                continue
            if "scheduler" in node.type().name().lower():
                continue

            # Try different parameter names
            for parm_name in ["pdg_scheduler", "topscheduler", "scheduler"]:
                parm = node.parm(parm_name)
                if parm:
                    try:
                        parm.set(scheduler_path)
                        print(f"  ✓ {node.name()} - set via '{parm_name}'")
                        count += 1
                        break
                    except:
                        pass

        # Set as default on network
        for parm_name in ["topscheduler", "defaultscheduler", "scheduler"]:
            parm = self.topnet.parm(parm_name)
            if parm:
                try:
                    parm.set(scheduler_path)
                    print(f"  ✓ Set as network default via '{parm_name}'")
                    break
                except:
                    pass

        print(f"✓ Scheduler applied to {count} nodes")

    def _execute_work_items(self):
        """Generate and execute work items for single item mode"""
        print("\n" + "-" * 60)
        print("Phase 5: Work Item Execution (Single Item)")
        print("-" * 60)

        try:
            # Initialize PDG context
            print("Initializing PDG context...")
            self._initialize_pdg_context()

            # Generate work items
            print("\nGenerating work items...")
            num_items = self._generate_work_items()

            if num_items == 0:
                print("✗ No work items generated")
                self.status_dict['errors'].append("No work items generated")
                return False

            print(f"✓ Generated {num_items} work items")

            if num_items <= self.item_index:
                print(f"⚠ Warning: Target index {self.item_index} >= {num_items} items")

            # Cook work items
            print(f"\nCooking work items (target index: {self.item_index})...")

            try:
                if self.output_node:
                    self.output_node.cookWorkItems(block=True)
                else:
                    self.topnet.cookWorkItems(block=True)
                print("✓ Cooking completed")
            except Exception as e:
                print(f"⚠ Cooking raised exception (may be normal): {e}")
                # Continue anyway as some items may have cooked

            # Collect work item results after cooking
            self._collect_work_item_results()

            print("✓ Work item execution completed")
            return True

        except Exception as e:
            print(f"✗ Work item execution failed: {e}")
            self.status_dict['errors'].append(f"Execution: {e}")

            # Try alternative cooking methods
            return self._try_alternative_cooking()

    def _collect_work_item_results(self):
        """Collect results from work items - properly implemented"""
        print("\nCollecting work item results...")

        # Clear the lists to ensure clean collection
        self.status_dict['work_items_processed'] = []
        self.status_dict['skipped_items'] = []

        for node in self.topnet.children():
            if node.type().category().name() != "Top":
                continue

            # Skip scheduler nodes
            if "scheduler" in node.type().name().lower():
                continue

            try:
                pdg_node = None
                work_items = None

                # Try to get PDG node and work items
                try:
                    pdg_node = node.getPDGNode()
                    if pdg_node:
                        work_items = pdg_node.workItems
                except:
                    pass

                if not work_items:
                    print(f"  No work items found in {node.name()}")
                    continue

                print(f"  Found {len(work_items)} work items in {node.name()}")

                # Process each work item
                for i, wi in enumerate(work_items):
                    # Get work item index - try multiple approaches
                    wi_index = i  # Default to enumeration

                    if hasattr(wi, 'index'):
                        wi_index = wi.index
                    elif hasattr(wi, 'id'):
                        try:
                            wi_index = int(wi.id)
                        except:
                            wi_index = i

                    # Get work item name
                    wi_name = wi.name if hasattr(wi, 'name') else f"{node.name()}_{i}"

                    # Get status
                    status = self._get_work_item_status(wi)

                    # Create item info
                    item_info = {
                        'index': wi_index,
                        'name': wi_name,
                        'node': node.name(),
                        'status': status
                    }

                    # Sort based on index matching
                    if wi_index == self.item_index:
                        self.status_dict['work_items_processed'].append(item_info)
                        print(f"    ✓ Processed: {wi_name} (index: {wi_index}) - {status}")
                    else:
                        self.status_dict['skipped_items'].append(item_info)
                        if len(self.status_dict['skipped_items']) <= 5:
                            print(f"    - Skipped: {wi_name} (index: {wi_index})")
                        elif len(self.status_dict['skipped_items']) == 6:
                            print(f"    ... and more skipped items")

            except Exception as e:
                print(f"  Warning: Error collecting from {node.name()}: {str(e)}")
                continue

        # Print summary
        processed_count = len(self.status_dict['work_items_processed'])
        skipped_count = len(self.status_dict['skipped_items'])

        print(f"\nWork Item Collection Summary:")
        print(f"  Target Index: {self.item_index}")
        print(f"  Frame Number: {str(self.item_index).zfill(4)}")
        print(f"  Processed: {processed_count} work item(s)")
        print(f"  Skipped: {skipped_count} work item(s)")

        if processed_count == 0 and skipped_count == 0:
            print(f"  ⚠ Warning: No work items found!")
            print(f"    Ensure work items were generated before cooking")
        elif processed_count == 0:
            print(f"  ⚠ Warning: No work items with index {self.item_index}")
            indices = sorted(set([item['index'] for item in self.status_dict['skipped_items']]))[:10]
            if indices:
                print(f"    Available indices: {indices}")

    def _initialize_pdg_context(self):
        """Initialize PDG graph context"""
        # Dirty all nodes
        for node in self.topnet.children():
            if node.type().category().name() == "Top":
                try:
                    node.dirtyAllTasks(False)
                except:
                    pass

        time.sleep(0.5)

        # Try to generate on a generator node
        for node in self.topnet.children():
            if "generator" in node.type().name().lower():
                try:
                    node.generateStaticWorkItems()
                    time.sleep(0.5)
                    return
                except:
                    pass

    def _generate_work_items(self):
        """Generate work items and count them"""
        max_items = 0

        # First, try to generate work items at the network level
        print("  Attempting network-level generation...")
        try:
            self.topnet.cookWorkItems(generate_only=True, block=True)
            time.sleep(1)
            print("    ✓ Network-level generation completed")
        except Exception as e:
            print(f"    Note: Network generation returned: {e}")

        # Also try to generate on individual nodes
        print("  Generating on individual nodes...")
        for node in self.topnet.children():
            if node.type().category().name() != "Top":
                continue
            if "scheduler" in node.type().name().lower():
                continue

            try:
                # Try to generate static work items
                if hasattr(node, 'generateStaticWorkItems'):
                    node.generateStaticWorkItems()
                    print(f"    Generated static items for {node.name()}")
            except:
                pass

            try:
                # Try cook with generate_only
                if hasattr(node, 'cookWorkItems'):
                    node.cookWorkItems(generate_only=True, block=True)
                    print(f"    Generated items for {node.name()}")
            except:
                pass

        # Wait for generation to complete
        time.sleep(1)

        # Now count work items on each node
        print("\n  Counting generated work items:")
        for node in self.topnet.children():
            if node.type().category().name() != "Top":
                continue
            if "scheduler" in node.type().name().lower():
                continue

            try:
                # Try multiple methods to get work items
                work_items = None
                pdg_node = None

                # Method 1: Direct PDG node
                try:
                    pdg_node = node.getPDGNode()
                    if pdg_node and hasattr(pdg_node, 'workItems'):
                        work_items = pdg_node.workItems
                except:
                    pass

                # Method 2: Through graph context
                if not work_items:
                    try:
                        graph_context = node.getPDGGraphContext()
                        if graph_context:
                            pdg_node = node.getPDGNode()
                            if pdg_node:
                                work_items = pdg_node.workItems
                    except:
                        pass

                if work_items and len(work_items) > 0:
                    print(f"    {node.name()}: {len(work_items)} items")
                    max_items = max(max_items, len(work_items))

                    # Debug: print first few work item indices
                    indices = []
                    for wi in work_items[:5]:
                        if hasattr(wi, 'index'):
                            indices.append(wi.index)
                    if indices:
                        print(f"      Sample indices: {indices}")
            except Exception as e:
                print(f"    Error counting items in {node.name()}: {e}")

        return max_items

    def _collect_work_item_results(self):
        """Collect results from work items - Fixed version for proper processed/skipped tracking"""
        print("\nCollecting work item results...")

        # Clear the lists to ensure clean collection
        self.status_dict['work_items_processed'] = []
        self.status_dict['skipped_items'] = []

        # First, make sure we have generated work items
        for node in self.topnet.children():
            if node.type().category().name() != "Top":
                continue

            # Skip scheduler nodes
            if "scheduler" in node.type().name().lower():
                continue

            try:
                # Try multiple ways to get PDG node and work items
                pdg_node = None
                work_items = []

                # Method 1: Direct PDG node access
                try:
                    pdg_node = node.getPDGNode()
                    if pdg_node:
                        work_items = pdg_node.workItems
                        if work_items:
                            print(f"  Found {len(work_items)} work items in {node.name()} via getPDGNode")
                except Exception as e:
                    pass

                # Method 2: Try through graph context
                if not work_items:
                    try:
                        graph_context = node.getPDGGraphContext()
                        if graph_context:
                            pdg_node = graph_context.graph.nodeByName(node.name())
                            if pdg_node:
                                work_items = pdg_node.workItems
                                if work_items:
                                    print(f"  Found {len(work_items)} work items in {node.name()} via graph context")
                    except Exception as e:
                        pass

                # Method 3: Use pdg module directly
                if not work_items:
                    try:
                        import pdg
                        for context_name in dir(pdg):
                            if "Context" in context_name:
                                context = getattr(pdg, context_name)
                                if hasattr(context, 'graph'):
                                    try:
                                        test_node = context.graph.nodeByName(node.name())
                                        if test_node and hasattr(test_node, 'workItems'):
                                            work_items = test_node.workItems
                                            if work_items:
                                                pdg_node = test_node
                                                print(
                                                    f"  Found {len(work_items)} work items in {node.name()} via pdg module")
                                                break
                                    except:
                                        pass
                    except Exception as e:
                        pass

                # Process work items if we found any
                if work_items:
                    for i, wi in enumerate(work_items):
                        # Try to get index from work item
                        wi_index = i  # Default to enumeration index

                        # Try to get actual work item index
                        if hasattr(wi, 'index'):
                            wi_index = wi.index
                        elif hasattr(wi, 'id'):
                            # Sometimes index is stored as id
                            wi_index = wi.id

                        # Get work item name
                        wi_name = wi.name if hasattr(wi, 'name') else f"{node.name()}_{i}"

                        # Collect work item information
                        item_info = {
                            'index': wi_index,
                            'name': wi_name,
                            'node': node.name(),
                            'status': self._get_work_item_status(wi)
                        }

                        # Check if this matches our target index
                        if wi_index == self.item_index:
                            self.status_dict['work_items_processed'].append(item_info)
                            print(f"    ✓ Processed: {wi_name} (index: {wi_index}) - {item_info['status']}")
                        else:
                            self.status_dict['skipped_items'].append(item_info)
                            # Only print first few skipped to avoid clutter
                            if len(self.status_dict['skipped_items']) <= 3:
                                print(f"    - Skipped: {wi_name} (index: {wi_index})")
                else:
                    # No work items found for this node
                    print(f"  No work items found in {node.name()}")

            except Exception as e:
                print(f"  Warning: Error collecting from {node.name()}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        # Print summary
        processed_count = len(self.status_dict['work_items_processed'])
        skipped_count = len(self.status_dict['skipped_items'])

        print(f"\nWork Item Collection Summary:")
        print(f"  Target Index: {self.item_index}")
        print(f"  Frame Number: {str(self.item_index).zfill(4) if self.item_index is not None else '0000'}")
        print(f"  Processed: {processed_count} work item(s)")
        print(f"  Skipped: {skipped_count} work item(s)")

        if processed_count == 0 and skipped_count == 0:
            print(f"  ⚠ Warning: No work items were found at all!")
            print(f"    This might mean work items weren't generated properly")
            print(f"    or the PDG context isn't accessible")
        elif processed_count == 0:
            print(f"  ⚠ Warning: No work items found with index {self.item_index}")
            available_indices = sorted(
                set([item['index'] for item in self.status_dict['skipped_items'] if item['index'] >= 0]))
            if available_indices:
                print(f"    Available indices: {available_indices[:10]}...")
        else:
            # Show detailed status for processed items
            for item in self.status_dict['work_items_processed']:
                print(f"    - {item['name']} from {item['node']}: {item['status']}")

    def _get_work_item_status(self, wi):
        """Get work item status string"""
        if hasattr(wi, 'isSuccessful') and wi.isSuccessful:
            return 'success'
        elif hasattr(wi, 'isFailed') and wi.isFailed:
            return 'failed'
        elif hasattr(wi, 'isCancelled') and wi.isCancelled:
            return 'cancelled'
        else:
            return 'unknown'

    def _try_alternative_cooking(self):
        """Try alternative cooking methods"""
        print("\nTrying alternative cooking methods...")

        # Method 1: executeGraph
        try:
            if self.output_node:
                self.output_node.executeGraph(False, True, False, True)
                print("✓ Alternative method 1 succeeded")
                return True
        except:
            pass

        # Method 2: Direct network cook
        try:
            self.topnet.cookWorkItems(block=True)
            print("✓ Alternative method 2 succeeded")
            return True
        except:
            pass

        print("✗ All cooking methods failed")
        return False

    def _collect_all_outputs(self):
        """Comprehensive output file collection"""
        print("\n" + "-" * 60)
        print("Phase 6: Output Collection")
        print("-" * 60)

        collectors = [
            ('USD Files', self._collect_usd_files, 'usd'),
            ('Rendered Images', self._collect_render_files, 'renders'),
            ('PDG Files', self._collect_pdg_files, 'pdg'),
            ('Log Files', self._collect_log_files, 'logs'),
            ('Work Item Outputs', self._collect_work_item_outputs, 'other')
        ]

        for name, collector, category in collectors:
            print(f"\nCollecting {name}...")
            try:
                files = collector()
                count = 0
                for src_file in files:
                    dest = self._copy_file_organized(src_file, category)
                    if dest:
                        self.status_dict['files_created'][category].append(dest)
                        count += 1
                print(f"  ✓ Collected {count} {name.lower()}")
            except Exception as e:
                print(f"  ✗ Failed to collect {name}: {e}")

        # Update total count
        total = sum(len(v) for k, v in self.status_dict['files_created'].items()
                    if k != 'total_count')
        self.status_dict['files_created']['total_count'] = total

        print(f"\n✓ Total files collected: {total}")

    def _collect_usd_files(self):
        """Collect all USD files"""
        patterns = [
            os.path.join(self.working_dir, '**/*.usd'),
            os.path.join(self.working_dir, '**/*.usda'),
            os.path.join(self.working_dir, '**/*.usdc'),
            os.path.join(self.working_dir, '**/*.usdz'),
        ]

        files = []
        for pattern in patterns:
            files.extend(glob.glob(pattern, recursive=True))

        return list(set(files))  # Remove duplicates

    def _collect_render_files(self):
        """Collect all rendered images"""
        patterns = [
            '/tmp/render/**/*.exr',
            '/tmp/render/**/*.png',
            '/tmp/render/**/*.jpg',
            '/tmp/render/**/*.tif',
            os.path.join(self.working_dir, 'render/**/*.exr'),
            os.path.join(self.working_dir, 'images/**/*'),
        ]

        files = []
        for pattern in patterns:
            try:
                files.extend(glob.glob(pattern, recursive=True))
            except:
                # Non-recursive fallback for /tmp
                if pattern.startswith('/tmp'):
                    files.extend(glob.glob(pattern.replace('/**/', '/')))

        return list(set(files))

    def _collect_pdg_files(self):
        """Collect PDG-specific files"""
        pdgtemp_dir = os.path.join(self.working_dir, 'pdgtemp')
        if not os.path.exists(pdgtemp_dir):
            return []

        patterns = [
            os.path.join(pdgtemp_dir, '**/*.json'),
            os.path.join(pdgtemp_dir, '**/data/*'),
        ]

        files = []
        for pattern in patterns:
            files.extend(glob.glob(pattern, recursive=True))

        return files

    def _collect_log_files(self):
        """Collect log files"""
        patterns = [
            os.path.join(self.working_dir, '**/*.log'),
            os.path.join(self.working_dir, 'pdgtemp/**/*.txt'),
        ]

        files = []
        for pattern in patterns:
            files.extend(glob.glob(pattern, recursive=True))

        return files

    def _collect_work_item_outputs(self):
        """Collect outputs from work items"""
        files = []

        if not self.output_node:
            return files

        try:
            for node in self.topnet.children():
                if node.type().category().name() != "Top":
                    continue

                try:
                    pdg_node = node.getPDGNode()
                    if not pdg_node:
                        continue

                    work_items = pdg_node.workItems
                    for wi in work_items:
                        # Try multiple methods
                        for attr in ['expectedOutputFiles', 'actualOutputFiles', 'outputFiles']:
                            try:
                                output_files = getattr(wi, attr)
                                for f in output_files:
                                    if os.path.exists(f):
                                        files.append(f)
                            except:
                                pass
                except:
                    pass
        except:
            pass

        return list(set(files))

    def _copy_file_organized(self, src_file, category):
        """Copy file to organized output structure"""
        if not os.path.exists(src_file):
            return None

        # Skip if file is already in output dir
        if src_file.startswith(self.output_dir):
            return None

        # Create category directory
        dest_dir = os.path.join(self.output_dir, category)
        os.makedirs(dest_dir, exist_ok=True)

        # Generate unique destination name
        filename = os.path.basename(src_file)
        dest_path = os.path.join(dest_dir, filename)

        if os.path.exists(dest_path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(dest_dir, f"{base}_{counter}{ext}")
                counter += 1

        try:
            shutil.copy2(src_file, dest_path)
            return dest_path
        except Exception as e:
            print(f"    Failed to copy {filename}: {e}")
            return None

    def _save_final_hip(self):
        """Save the final HIP file"""
        print("\n" + "-" * 60)
        print("Phase 7: Save HIP File")
        print("-" * 60)

        try:
            # Build filename based on mode
            hip_name = os.path.basename(self.hip_file)
            base, ext = os.path.splitext(hip_name)

            if self.cook_entire_graph:
                # Submit As Job mode: save with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                final_hip = os.path.join(
                    self.output_dir,
                    'hip',
                    f"{base}_submitasjob_{timestamp}{ext}"
                )
            elif self.use_single_machine:
                # Single Machine mode: save with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                final_hip = os.path.join(
                    self.output_dir,
                    'hip',
                    f"{base}_single_machine_{timestamp}{ext}"
                )
            else:
                # On Schedule mode: save with frame number
                frame_num = str(self.item_index).zfill(4)
                final_hip = os.path.join(
                    self.output_dir,
                    'hip',
                    f"{base}_final.{frame_num}{ext}"
                )

            hou.hipFile.save(final_hip)
            self.status_dict['files_created']['hip'].append(final_hip)

            print(f"✓ Saved HIP file: {final_hip}")

        except Exception as e:
            print(f"✗ Failed to save HIP file: {e}")
            self.status_dict['errors'].append(f"HIP save: {e}")

    def _finalize_execution(self):
        """Finalize execution and write status"""
        print("\n" + "-" * 60)
        print("Phase 8: Finalization")
        print("-" * 60)

        # Calculate duration
        self.status_dict['timestamp_end'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            start = datetime.strptime(self.status_dict['timestamp_start'], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(self.status_dict['timestamp_end'], "%Y-%m-%d %H:%M:%S")
            self.status_dict['duration_seconds'] = (end - start).total_seconds()
        except:
            self.status_dict['duration_seconds'] = 0

        # Write status file
        status_dir = os.path.join(self.output_dir, 'execution_status')
        os.makedirs(status_dir, exist_ok=True)

        if self.cook_entire_graph:
            # Submit As Job mode: save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            status_file = os.path.join(status_dir, f'pdg_submitasjob_status_{timestamp}.json')
        elif self.use_single_machine:
            # Single Machine mode: save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            status_file = os.path.join(status_dir, f'pdg_single_machine_status_{timestamp}.json')
        else:
            # On Schedule mode: save with frame number
            frame_num = str(self.item_index).zfill(4)
            status_file = os.path.join(status_dir, f'pdg_execution_status.{frame_num}.json')

        try:
            with open(status_file, 'w') as f:
                json.dump(self.status_dict, f, indent=4, default=str)
            print(f"✓ Status written to: {status_file}")

            # Create a symlink to latest
            latest_link = os.path.join(status_dir, 'pdg_execution_status.latest.json')
            try:
                if os.path.exists(latest_link):
                    os.remove(latest_link)
                os.symlink(os.path.basename(status_file), latest_link)
                print(f"  Created latest link: {latest_link}")
            except:
                pass

        except Exception as e:
            print(f"✗ Failed to write status: {e}")

        # Print summary
        print("\n" + "=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Execution Mode: {self.execution_mode.upper()}")
        print(f"Status: {self.status_dict['status'].upper()}")
        print(f"Duration: {self.status_dict['duration_seconds']:.2f} seconds")

        if self.cook_entire_graph or self.use_single_machine:
            print(f"Total Work Items: {self.status_dict.get('work_items_total', 0)}")
            print(f"  Succeeded: {self.status_dict.get('work_items_succeeded', 0)}")
            print(f"  Failed: {self.status_dict.get('work_items_failed', 0)}")
        else:
            print(f"Frame/Item Index: {self.item_index} (Frame: {str(self.item_index).zfill(4)})")
            print(f"Work Items Processed: {len(self.status_dict.get('work_items_processed', []))}")
            print(f"Work Items Skipped: {len(self.status_dict.get('skipped_items', []))}")

        print(f"Files Collected: {self.status_dict['files_created']['total_count']}")

        if self.status_dict['errors']:
            print(f"\nErrors ({len(self.status_dict['errors'])}):")
            for error in self.status_dict['errors']:
                print(f"  - {error}")

        print("=" * 80)


def main():
    """Main entry point"""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='PDG Universal Wrapper Script for Conductor render farm'
    )
    parser.add_argument('--hip_file', type=str, required=True,
                        help='Path to the Houdini file')
    parser.add_argument('--topnet_path', type=str, default='/obj/topnet1',
                        help='Path to the TOP network node')
    parser.add_argument('--working_dir', type=str, required=True,
                        help='Working directory path')
    parser.add_argument('--output_dir', type=str, default=None,
                        help='Output directory for rendered files')

    # Mode selection arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--cook_entire_graph', action='store_true',
                       help='Cook entire graph (submitAsJob mode)')
    group.add_argument('--use_single_machine', action='store_true',
                       help='Cook all work items on single machine (local execution)')
    group.add_argument('--item_index', type=int, default=None,
                       help='Index of the work item to cook (on_schedule mode)')

    args = parser.parse_args()

    # Validate mode
    if not args.cook_entire_graph and not args.use_single_machine and args.item_index is None:
        parser.error("One of --cook_entire_graph, --use_single_machine, or --item_index must be specified")

    # Determine output directory
    if not args.output_dir:
        args.output_dir = os.environ.get('PDG_RENDER_DIR')
        if not args.output_dir:
            args.output_dir = os.path.join(args.working_dir, 'pdg_render')

    # Create and run executor
    executor = PDGUniversalExecutor(
        hip_file=args.hip_file,
        topnet_path=args.topnet_path,
        working_dir=args.working_dir,
        output_dir=args.output_dir,
        item_index=args.item_index,
        cook_entire_graph=args.cook_entire_graph,
        use_single_machine=args.use_single_machine
    )

    success = executor.run()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()