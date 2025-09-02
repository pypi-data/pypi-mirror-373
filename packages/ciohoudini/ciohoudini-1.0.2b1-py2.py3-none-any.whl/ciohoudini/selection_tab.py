"""
Houdini Conductor Selection Tab UI

This module defines the SelectionTab class, a PySide2-based UI component for selecting
Houdini nodes within subnets for submission to Conductor. It provides a scrollable panel
with checkboxes for nodes and subnets, global select/deselect buttons, and functionality
to generate payloads for selected nodes.

Dependencies:
- PySide2: QtWidgets, QtCore for UI components
- ciohoudini: Custom Houdini utilities (buttoned_scroll_panel, rops, validation, payload)
- ciocore.loggeria: Custom logging for Conductor
"""

from PySide2 import QtWidgets, QtCore
from ciohoudini.buttoned_scroll_panel import ButtonedScrollPanel
from ciohoudini import rops, validation, payload

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

class SelectionTab(ButtonedScrollPanel):
    """
    A UI tab for selecting Houdini nodes within subnets for Conductor submission.

    Attributes:
        dialog: The parent dialog containing this tab.
        node: The Houdini node associated with the dialog.
        all_checkboxes (list): List of all node checkboxes.
        node_map (dict): Maps checkboxes to their corresponding Houdini nodes.
        subnet_checkboxes (list): List of all subnet checkboxes.
    """
    def __init__(self, dialog):
        """
        Initializes the SelectionTab with a buttoned scroll panel and global buttons.

        Args:
            dialog: The parent dialog containing this tab.
        """
        super(SelectionTab, self).__init__(
            dialog,
            buttons=[("close", "Close"), ("continue", "Continue Submission")]
        )
        self.dialog = dialog
        self.node = self.dialog.node
        self.all_checkboxes = []  # Track all node checkboxes
        self.node_map = {}  # Map checkboxes to nodes
        self.subnet_checkboxes = []  # Track subnet checkboxes
        self.configure_signals()

        # Add global select/deselect buttons
        self.add_global_buttons()

    def configure_signals(self):
        """Connects button signals to their respective handlers."""
        self.buttons["close"].clicked.connect(self.dialog.on_close)
        self.buttons["continue"].clicked.connect(self.on_continue)

    def add_global_buttons(self):
        """Adds global buttons for selecting and deselecting all nodes."""
        button_layout = QtWidgets.QHBoxLayout()
        select_all_button = QtWidgets.QPushButton("Select all nodes")
        deselect_all_button = QtWidgets.QPushButton("Deselect all nodes")

        # Connect buttons to their handlers
        select_all_button.clicked.connect(self.select_all_nodes)
        deselect_all_button.clicked.connect(self.deselect_all_nodes)

        # Add buttons to the layout
        button_layout.addWidget(select_all_button)
        button_layout.addWidget(deselect_all_button)
        self.layout.addLayout(button_layout)

    def list_subnet_nodes(self, node):
        """
        Lists subnets connected to the generator node and adds checkboxes for their child nodes.

        Args:
            node (hou.Node): The Houdini node to inspect for connected subnets.
        """
        logger.debug("Selection tab: Listing subnet nodes...")
        if not node:
            logger.debug("Selection tab: No node provided.")
            return

        # Clear existing content and reset tracking lists
        self.clear()
        self.all_checkboxes = []
        self.node_map = {}
        self.subnet_checkboxes = []

        # Re-add global buttons
        self.add_global_buttons()

        # Iterate over connected output nodes to find subnets
        for output_node in node.outputs():
            if output_node and output_node.type().name() == "subnet":
                logger.debug(f"Found subnet: {output_node.name()}")

                # Create a horizontal layout for subnet title and checkbox
                subnet_row_layout = QtWidgets.QHBoxLayout()

                # Create and configure subnet checkbox
                subnet_checkbox = QtWidgets.QCheckBox()
                subnet_checkbox.setToolTip(f"Toggle all nodes in subnet: {output_node.name()}")
                subnet_row_layout.addWidget(subnet_checkbox)
                self.subnet_checkboxes.append(subnet_checkbox)

                # Create and style subnet name label
                subnet_name_label = QtWidgets.QLabel(f"Subnet: {output_node.name()}")
                subnet_name_label.setStyleSheet("font-weight: bold;")
                subnet_row_layout.addWidget(subnet_name_label)

                # Align subnet row to the left
                subnet_row_layout.setAlignment(QtCore.Qt.AlignLeft)
                self.layout.addLayout(subnet_row_layout)

                # Create a vertical layout for node checkboxes
                node_container_layout = QtWidgets.QVBoxLayout()
                node_container_layout.setContentsMargins(40, 0, 0, 0)  # Indent for hierarchy
                self.layout.addLayout(node_container_layout)

                # Add checkboxes for each child node in the subnet
                node_checkboxes = []
                for child_node in output_node.children():
                    checkbox = QtWidgets.QCheckBox(child_node.name())
                    node_container_layout.addWidget(checkbox)
                    node_checkboxes.append(checkbox)
                    self.all_checkboxes.append(checkbox)
                    self.node_map[checkbox] = child_node

                # Connect subnet checkbox to toggle child nodes
                subnet_checkbox.stateChanged.connect(
                    lambda state, cb=node_checkboxes: self.toggle_subnet_nodes(state, cb)
                )

        # Add stretch to push content to the top
        self.layout.addStretch()

    def toggle_subnet_nodes(self, state, checkboxes):
        """
        Toggles the state of all node checkboxes under a subnet.

        Args:
            state (int): The state of the subnet checkbox (0: unchecked, 2: checked).
            checkboxes (list): List of node checkboxes under the subnet.
        """
        is_checked = state == QtCore.Qt.Checked
        for checkbox in checkboxes:
            checkbox.setChecked(is_checked)

    def select_all_nodes(self):
        """Checks all node and subnet checkboxes."""
        logger.debug("Selecting all nodes...")
        for checkbox in self.all_checkboxes:
            checkbox.setChecked(True)
        for subnet_checkbox in self.subnet_checkboxes:
            subnet_checkbox.setChecked(True)

    def deselect_all_nodes(self):
        """Unchecks all node and subnet checkboxes."""
        logger.debug("Deselecting all nodes...")
        for checkbox in self.all_checkboxes:
            checkbox.setChecked(False)
        for subnet_checkbox in self.subnet_checkboxes:
            subnet_checkbox.setChecked(False)

    def get_payloads(self):
        """
        Generates payloads for all checked nodes.

        Returns:
            list: A list of payloads for selected nodes.
        """
        logger.debug("Generating payloads for all checked nodes...")
        payload_list = []
        kwargs = {}

        for checkbox, node in self.node_map.items():
            if checkbox.isChecked():
                logger.debug(f"Generating payload for node: {node.name()}")
                frame_range = rops.get_parameter_value(node, "frame_range")
                rop_path = rops.get_parameter_value(node, "driver_path")
                kwargs["frame_range"] = frame_range
                kwargs["task_limit"] = -1  # Unlimited tasks
                kwargs["do_asset_scan"] = True
                try:
                    node_payload = payload.get_payload(node, rop_path, **kwargs)
                    if node_payload:
                        payload_list.append(node_payload)
                except Exception as e:
                    logger.error(f"Error generating payload for node {node.name()}: {e}")

        return payload_list

    def on_continue(self):
        """Handles the 'Continue Submission' button click, generating payloads and showing validation tab."""
        logger.debug("Validation tab: Continue Submission...")

        # Generate payloads for checked nodes
        self.dialog.payloads = self.get_payloads()
        logger.debug(f"Generated {len(self.dialog.payloads)} payloads.")

        if self.node:
            # Switch to the validation tab
            self.dialog.show_validation_tab()
            logger.debug("Validation tab: Running validation...")

            # Run validation and populate results
            errors, warnings, notices = validation.run(self.node)
            logger.debug("Validation tab: Populating validation results...")
            self.dialog.validation_tab.populate(errors, warnings, notices)