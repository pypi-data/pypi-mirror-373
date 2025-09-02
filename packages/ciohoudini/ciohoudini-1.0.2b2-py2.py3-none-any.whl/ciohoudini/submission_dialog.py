"""
Houdini Conductor Submission Dialog

This module defines the SubmissionDialog class, a PySide2-based dialog for managing
Conductor submissions in Houdini. It provides a tabbed interface for node selection,
validation, progress tracking, and response display.

Dependencies:
- hou: Houdini Python module
- PySide2: QtWidgets, QtCore, QtGui for UI components
- ciohoudini: Custom Houdini utilities (selection_tab, validation_tab, progress_tab, response_tab, validation, rops)
- ciocore.loggeria: Custom logging for Conductor
- time: Standard library for sleep functionality
"""

import hou
from PySide2 import QtWidgets, QtCore, QtGui

from ciohoudini.selection_tab import SelectionTab
from ciohoudini.validation_tab import ValidationTab
from ciohoudini.progress_tab import ProgressTab
from ciohoudini.response_tab import ResponseTab
from ciohoudini import validation, rops
import time

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

class SubmissionDialog(QtWidgets.QDialog):
    """
    A dialog for managing Conductor submissions with tabs for selection, validation, progress, and response.

    Attributes:
        node: The Houdini node associated with the dialog.
        payloads: List of generated payloads for submission.
        tab_widget: The QTabWidget containing all tabs.
        selection_tab: Tab for selecting nodes within subnets.
        validation_tab: Tab for displaying validation results.
        progress_tab: Tab for tracking submission progress.
        response_tab: Tab for displaying submission responses.
    """
    def __init__(self, nodes, payloads=None,parent=None):
        """
        Initializes the SubmissionDialog with a tabbed interface.

        Args:
            nodes (list): List of Houdini nodes, with the first node used for the dialog.
            parent (QWidget, optional): Parent widget for the dialog.
        """
        super(SubmissionDialog, self).__init__(parent)
        self.setWindowTitle("Conductor Submission")
        self.setStyleSheet(hou.qt.styleSheet())


        # Set up main layout and tab widget
        self.layout = QtWidgets.QVBoxLayout()
        self.tab_widget = QtWidgets.QTabWidget()
        self.setLayout(self.layout)
        self.layout.addWidget(self.tab_widget)

        # Initialize node and payloads
        self.node = nodes[0] if nodes else None
        logger.debug(f"SubmissionDialog: Node name: {self.node.name()}")
        logger.debug(f"SubmissionDialog: Node type: {self.node.type().name()}")
        self.payloads = payloads

        # Create and add tabs
        self.selection_tab = SelectionTab(self)
        self.tab_widget.addTab(self.selection_tab, "Selection")
        self.selection_tab.hide()

        self.validation_tab = ValidationTab(self)
        self.tab_widget.addTab(self.validation_tab, "Validation")

        self.progress_tab = ProgressTab(self)
        self.tab_widget.addTab(self.progress_tab, "Progress")

        self.response_tab = ResponseTab(self)
        self.tab_widget.addTab(self.response_tab, "Response")

        # Configure dialog properties
        self.setMinimumSize(1200, 742)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Initialize selection tab and run initial logic
        self.create_selection_tab(self.node)
        self.run(self.node)

    def is_generation_node(self, node):
        """
        Checks if the node is a generator node.

        Args:
            node (hou.Node): The Houdini node to check.

        Returns:
            bool: True if the node is a generator node, False otherwise.
        """
        if node:
            node_type = rops.get_node_type(node)
            if node_type in ["generator"]:
                return True
        return False

    def create_selection_tab(self, node):
        """
        Shows the selection tab if the node is a generator node.

        Args:
            node (hou.Node): The Houdini node to check.
        """
        is_generation_node = self.is_generation_node(node)
        if is_generation_node:
            self.selection_tab.show()

    def show_selection_tab(self):
        """Activates and displays the selection tab, disabling other tabs."""
        self.tab_widget.setTabEnabled(0, True)
        self.tab_widget.setCurrentWidget(self.selection_tab)
        self.tab_widget.setTabEnabled(1, False)
        self.tab_widget.setTabEnabled(2, False)
        self.tab_widget.setTabEnabled(3, False)
        QtCore.QCoreApplication.processEvents()

    def show_validation_tab(self):
        """Activates and displays the validation tab, disabling other tabs."""
        self.tab_widget.setTabEnabled(0, False)
        self.tab_widget.setTabEnabled(1, True)
        self.tab_widget.setCurrentWidget(self.validation_tab)
        self.tab_widget.setTabEnabled(2, False)
        self.tab_widget.setTabEnabled(3, False)
        QtCore.QCoreApplication.processEvents()

    def show_progress_tab(self):
        """Activates and displays the progress tab, disabling other tabs."""
        self.tab_widget.setTabEnabled(2, True)
        self.tab_widget.setCurrentWidget(self.progress_tab)
        self.tab_widget.setTabEnabled(0, False)
        self.tab_widget.setTabEnabled(1, False)
        self.tab_widget.setTabEnabled(3, False)
        QtCore.QCoreApplication.processEvents()
        time.sleep(1)

    def show_response_tab(self):
        """Activates and displays the response tab, disabling other tabs."""
        self.tab_widget.setTabEnabled(3, True)
        self.tab_widget.setCurrentWidget(self.response_tab)
        self.tab_widget.setTabEnabled(0, False)
        self.tab_widget.setTabEnabled(1, False)
        self.tab_widget.setTabEnabled(2, True)
        QtCore.QCoreApplication.processEvents()
        time.sleep(1)

    def run(self, node):
        """
        Initializes the dialog based on the node type, showing the appropriate tab.

        Args:
            node (hou.Node): The Houdini node to process.
        """
        if not self.is_generation_node(node):
            logger.debug("Not a generator node, running validation...")
            self.show_validation_tab()
            errors, warnings, notices = validation.run(self.node)
            self.validation_tab.populate(errors, warnings, notices)
        else:
            logger.debug("Generator node, skipping validation...")
            self.show_selection_tab()
            self.selection_tab.list_subnet_nodes(node)

    def on_close(self):
        """Closes the dialog."""
        self.accept()