
import hou

from ciohoudini import rops


def browse_usd_file(node, **kwargs):
    """
    Open a file browser to select a USD file and set it in the node's parameters.

    Validates that the selected file has a valid USD extension (.usd, .usda, .usdc, .usdz)
    and updates the node's usd_filepath parameter.

    Args:
        node: Houdini node to set the USD file path for.
        **kwargs: Additional arguments (unused).

    Returns:
        str: The selected file path, or None if the selection is canceled or invalid.
    """
    # Define valid USD file extensions
    valid_extensions = (".usd", ".usda", ".usdc", ".usdz")

    # Open file browser for single file selection
    file_path = hou.ui.selectFile(
        title="Browse for a USD file to upload",
        file_type=hou.fileType.Any,
        chooser_mode=hou.fileChooserMode.Read,
        multiple_select=False,
    )

    if not file_path:
        # User canceled the file selection
        return

    file_path = file_path.strip()

    # Validate file extension
    if not file_path.lower().endswith(valid_extensions):
        hou.ui.displayMessage(
            f"Invalid file type selected.\nPlease select a file with one of the following extensions: {', '.join(valid_extensions)}",
            title="Invalid File Type",
        )
        return

    # Set the file path in the node's usd_filepath parameter
    rops.set_parameter_value(node, "usd_filepath", file_path)
    # logger.debug("Selected USD file: ", file_path)

    return file_path