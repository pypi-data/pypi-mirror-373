"""
Module for post-installation setup of the Conductor plugin for Houdini.

This module configures Houdini package files to integrate the Conductor plugin by setting
environment variables and paths in the user's Houdini preferences directory.
"""

import platform
import os
import glob
import sys
import errno
import json

# Directory containing this script (ciohoudini package directory)
PKG_DIR = os.path.dirname(os.path.abspath(__file__))

# Parent directory of the package (Conductor root directory)
CIO_DIR = os.path.dirname(PKG_DIR).replace("\\", "/")

# Name of the package directory (ciohoudini)
PKGNAME = os.path.basename(PKG_DIR)

# Current platform (e.g., 'darwin', 'win32', 'linux')
PLATFORM = sys.platform

# Read version from VERSION file
with open(os.path.join(PKG_DIR, 'VERSION')) as version_file:
    VERSION = version_file.read().strip()

# Windows constants for SHGetFolderPathW
WIN_MY_DOCUMENTS = 5
WIN_TYPE_CURRENT = 0

# Determine Houdini path based on development or production environment
if os.environ.get("CIO_FEATURE_DEV"):
    houdini_path = os.path.join(os.environ.get("CIO"), "ciohoudini", "ciohoudini")
else:
    houdini_path = "$CIODIR/ciohoudini"

# Package file content for Houdini configuration
PACKAGE_FILE_CONTENT = {
    "env": [
        {
            "CIODIR": CIO_DIR
        },
        {
            "var": "HOUDINI_PATH",
            "value": [
                houdini_path
            ]
        },
        {
            "PYTHONPATH": {
                "method": "prepend",
                "value": [
                    "$CIODIR"
                ]
            }
        }
    ]
}


def main():
    """
    Main function to set up Conductor package files in Houdini preferences.

    Creates or updates conductor.json files in the user's Houdini packages directory
    for supported platforms (macOS, Windows, Linux).
    """
    # Check for supported platform
    if not PLATFORM in ["darwin", "win32", "linux"]:
        sys.stderr.write(f"Unsupported platform: {PLATFORM}")
        sys.exit(1)

    # Get list of package file paths
    package_files = get_package_files()
    if not package_files:
        # Handle case where package directory is not found
        sys.stderr.write("***************************.\n")
        sys.stderr.write("Could not find your Houdini packages folder.\n")
        sys.stderr.write("You will need to copy over the Conductor package JSON manually, like so:\n")
        sys.stderr.write("Go to your houdini prefs folder and create a folder there called packages.\n")
        pkg_file = os.path.join(CIO_DIR, "conductor.json")
        sys.stderr.write(f"Copy this file there {pkg_file}.\n")
        # Write default package file
        with open(pkg_file, 'w') as f:
            json.dump(PACKAGE_FILE_CONTENT, f, indent=4)
        sys.stderr.write("***************************.\n")
        sys.stderr.write("\n")
        sys.exit(1)

    # Process each package file
    for pkg_file in package_files:
        pkg_file = pkg_file.replace("\\", "/")
        folder = os.path.dirname(pkg_file)
        try:
            # Ensure package directory exists
            ensure_directory(folder)
        except BaseException:
            sys.stderr.write(f"Could not create directory: {folder}. Skipping\n")
            continue

        # Write package file with configuration
        with open(pkg_file, 'w') as f:
            json.dump(PACKAGE_FILE_CONTENT, f, indent=4)

        sys.stdout.write(f"Added Conductor Houdini package file: {pkg_file}")


def get_package_files():
    """
    Retrieve paths for Houdini package files based on the platform.

    Returns:
        list: List of paths to conductor.json files in Houdini preferences directories.
    """
    # Define pattern for Houdini preferences directory based on platform
    if PLATFORM == "darwin":
        pattern = os.path.expanduser("~/Library/Preferences/houdini/[0-9][0-9]*")
    elif PLATFORM == "linux":
        pattern = os.path.expanduser("~/houdini[0-9][0-9]*")
    else:  # windows
        import ctypes.wintypes
        # Get Windows My Documents path
        buff = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, WIN_MY_DOCUMENTS, None, WIN_TYPE_CURRENT, buff)
        documents = buff.value
        pattern = f"{documents}/houdini[0-9][0-9]*"

    # Return list of conductor.json file paths
    return [os.path.join(p, "packages", "conductor.json") for p in glob.glob(pattern)]


def ensure_directory(directory):
    """
    Ensure the specified directory exists, creating it if necessary.

    Args:
        directory: Path to the directory to create.

    Raises:
        OSError: If directory creation fails for reasons other than it already existing.
    """
    try:
        os.makedirs(directory)
    except OSError as ex:
        # Ignore error if directory already exists
        if ex.errno == errno.EEXIST and os.path.isdir(directory):
            sys.stderr.write(f"All good! Directory exists: {directory}\n")
            pass
        else:
            raise


if __name__ == '__main__':
    main()