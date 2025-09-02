import os
from ciohoudini import (
    controller,
    rops,
)
from ciocore import data as coredata


def connect_to_conductor(node):
    """Connect to Conductor and ensure valid connection before proceeding"""
    if not node:
        print(f"ERROR: Node is unavailable: {node}")
        raise RuntimeError("Cannot connect to Conductor without a valid node")

    # Check if already connected
    if coredata.valid():
        print(f"  Already connected to Conductor")
        return True

    print(f"  Connecting to Conductor...")
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        print(f"  Connection attempt {attempt}/{max_attempts}")

        try:
            kwargs = {
                "force": True
            }
            controller.connect(node, **kwargs)

            # Verify the connection was successful
            if coredata.valid():
                print(f"  ✓ Successfully connected to Conductor")
                return True
            else:
                print(f"  ✗ Connection attempt {attempt} failed - data not valid")
                if attempt < max_attempts:
                    import time
                    wait_time = attempt * 2  # Exponential backoff
                    print(f"  Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)

        except Exception as e:
            print(f"  ✗ Connection attempt {attempt} failed with error: {e}")
            if attempt < max_attempts:
                import time
                wait_time = attempt * 2
                print(f"  Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)

    # All attempts failed
    error_msg = "Failed to connect to Conductor after {} attempts. Please check your network connection and credentials.".format(
        max_attempts)
    print(f"  ERROR: {error_msg}")

    # Check if we should show UI message
    try:
        import hou
        if hou.isUIAvailable():
            hou.ui.displayMessage(
                error_msg,
                severity=hou.severityType.Error
            )
    except:
        pass  # If hou not available or UI not available, just continue

    raise RuntimeError(error_msg)


def get_hhp_dir(hfs):
    """Determine the HHP (Houdini Python Path) directory based on HFS and Houdini version

    Args:
        hfs: The HFS path (optional, will use environment variable if not provided)

    Returns:
        str: The path to the Houdini Python libs directory
    """
    if not hfs:
        hfs = os.environ.get('HFS', '/opt/sidefx/houdini/20/houdini-20.5.522-gcc11.2')

    # Extract version from HFS path
    # Common patterns:
    # /opt/sidefx/houdini/20/houdini-20.5.522-gcc11.2
    # /Applications/Houdini/Houdini20.5.522/Frameworks/Houdini.framework/Versions/20.5/Resources

    hhp_dir = None

    # Try to extract version number from path
    import re
    version_match = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', hfs)

    if version_match:
        major = int(version_match.group(1))
        minor = int(version_match.group(2))

        # Map Houdini version to Python version
        if major >= 20 and minor >= 5:
            # Houdini 20.5+ uses Python 3.11
            hhp_dir = os.path.join(hfs, 'houdini', 'python3.11libs')
        elif major >= 20:
            # Houdini 20.0 uses Python 3.10
            hhp_dir = os.path.join(hfs, 'houdini', 'python3.10libs')
        elif major >= 19 and minor >= 5:
            # Houdini 19.5 uses Python 3.9
            hhp_dir = os.path.join(hfs, 'houdini', 'python3.9libs')
        elif major >= 19:
            # Houdini 19.0 uses Python 3.7
            hhp_dir = os.path.join(hfs, 'houdini', 'python3.7libs')
        elif major >= 18 and minor >= 5:
            # Houdini 18.5 uses Python 3.7
            hhp_dir = os.path.join(hfs, 'houdini', 'python3.7libs')
        elif major >= 18:
            # Houdini 18.0 uses Python 2.7
            hhp_dir = os.path.join(hfs, 'houdini', 'python2.7libs')
        else:
            # Older versions use Python 2.7
            hhp_dir = os.path.join(hfs, 'houdini', 'python2.7libs')

    # Fallback: try to detect by checking which directory exists locally
    # This only works if running on a machine with Houdini installed
    if not hhp_dir or not os.path.exists(hhp_dir):
        possible_dirs = [
            'python3.11libs',
            'python3.10libs',
            'python3.9libs',
            'python3.7libs',
            'python2.7libs'
        ]

        for py_dir in possible_dirs:
            test_path = os.path.join(hfs, 'houdini', py_dir)
            if os.path.exists(test_path):
                hhp_dir = test_path
                break

    # Final fallback - use most recent Python version
    if not hhp_dir:
        hhp_dir = os.path.join(hfs, 'houdini', 'python3.11libs')
        print(f"  WARNING: Could not determine Python version, defaulting to python3.11libs")

    return hhp_dir


def configure_threading_environment(node, use_multiple_machines, job_env):
    """Configure threading environment variables for single machine execution

    Args:
        node: The scheduler node containing parameters
        use_multiple_machines: Boolean indicating if using multiple machines
        job_env: Dictionary of environment variables to update

    Returns:
        dict: Updated job_env with threading configuration
    """
    use_threading = rops.get_parameter_value(node, "use_threading")

    if not use_multiple_machines and use_threading:
        print(f"  Enabling multi-threading for single machine execution")

        # Get thread count - could be from parameter or auto-detect
        # Try to get from parameter first, otherwise use a reasonable default
        thread_count = rops.get_parameter_value(node, "houdini_max_threads")
        if not thread_count:
            # Default to 16 threads if not specified
            # In production, you might want to detect the actual core count on the target machine
            thread_count = 16

        thread_count_str = str(thread_count)

        # Core Houdini threading
        job_env["HOUDINI_MAXTHREADS"] = thread_count_str
        job_env["HOUDINI_THREADED_COOK"] = "1"

        # PDG threading - set slots to allow multiple work items to run concurrently
        # Use half the threads for PDG slots to balance threading vs parallelism
        pdg_slots = max(1, thread_count // 2)
        job_env["PDG_SLOTS"] = str(pdg_slots)
        job_env["PDG_MAXPROCS"] = thread_count_str

        # VEX threading
        job_env["HOUDINI_VEX_THREADED"] = "1"
        job_env["HOUDINI_VEX_MAXTHREADS"] = thread_count_str

        # Mantra threading (if rendering)
        job_env["MANTRA_THREADS"] = thread_count_str
        job_env["MANTRA_NONRAT_THREADS"] = thread_count_str

        # USD/Hydra threading (for Karma/USD workflows)
        job_env["PXR_WORK_THREAD_LIMIT"] = thread_count_str
        job_env["USD_SCHEDULER_THREADS"] = thread_count_str

        # Redshift threading
        job_env["REDSHIFT_COREMAXTHREADS"] = thread_count_str
        # Enable all available GPUs (0,1,2,3 for 4 GPUs)
        # You may want to make this configurable based on available GPUs
        job_env["REDSHIFT_GPUDEVICES"] = "0"  # Default to first GPU
        job_env["REDSHIFT_PREFERGPUS"] = "1"  # Prefer GPU rendering

        # Arnold threading
        job_env["ARNOLD_THREADS"] = thread_count_str
        job_env["ARNOLD_THREAD_PRIORITY"] = "normal"
        # Disable auto threads since we're explicitly setting them
        job_env["ARNOLD_AUTO_THREADS"] = "0"

        # V-Ray threading
        job_env["VRAY_NUM_THREADS"] = thread_count_str
        job_env["VRAY_USE_THREAD_AFFINITY"] = "1"  # Enable thread affinity for better performance
        job_env["VRAY_LOW_THREAD_PRIORITY"] = "0"  # Normal priority

        # RenderMan (PRMan) threading
        job_env["PRMAN_NTHREADS"] = thread_count_str
        job_env["RMAN_NTHREADS"] = thread_count_str  # Alternative env var for newer versions
        # RenderMan also uses these for advanced control
        job_env["RMAN_TRACE_MEMORY"] = "0"  # Disable memory tracing for performance

        # OpenCL for GPU acceleration (default to first device)
        job_env["HOUDINI_OCL_DEVICENUMBER"] = "0"

        # Memory management - set reasonable cache sizes
        job_env["HOUDINI_TEXTURE_CACHE_SIZE"] = "4096"  # 4GB texture cache
        job_env["HOUDINI_GEOMETRY_CACHE_SIZE"] = "2048"  # 2GB geometry cache

        print(f"  Threading configuration:")
        print(f"    Thread count: {thread_count}")
        print(f"    PDG slots: {pdg_slots}")
        print(f"    Houdini max threads: {thread_count}")
        print(f"    VEX threads: {thread_count}")
        print(f"    Mantra threads: {thread_count}")
        print(f"    Redshift threads: {thread_count}")
        print(f"    Arnold threads: {thread_count}")
        print(f"    V-Ray threads: {thread_count}")
        print(f"    RenderMan threads: {thread_count}")

    return job_env

def get_parameter_value(node, param_name, default_value):
    """
    Get the value
    """
    value = rops.get_parameter_value(node, param_name)
    if not value:
        value = default_value

    value_str = str(value)
    return value_str