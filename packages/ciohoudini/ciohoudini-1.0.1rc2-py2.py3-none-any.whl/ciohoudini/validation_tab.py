"""
Houdini Conductor Validation Tab UI

This module defines the ValidationTab class, a PySide2-based UI component for displaying
validation results in the Conductor submission process. It presents errors, warnings, and
informational notices in a scrollable panel and controls the submission flow based on validation outcomes.

Dependencies:
- ciohoudini: Custom Houdini utilities (buttoned_scroll_panel, notice_grp, rops)
- ciocore.loggeria: Custom logging for Conductor
"""

from ciohoudini.components.buttoned_scroll_panel import ButtonedScrollPanel
from ciohoudini.notice_grp import NoticeGrp
from ciohoudini import rops

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

class ValidationTab(ButtonedScrollPanel):
    """
    A UI tab for displaying validation results during Conductor submission.

    Attributes:
        dialog: The parent dialog containing this tab.
        buttons: Dictionary of buttons (close, continue) inherited from ButtonedScrollPanel.
    """
    def __init__(self, dialog):
        """
        Initializes the ValidationTab with a buttoned scroll panel and button signals.

        Args:
            dialog: The parent dialog containing this tab.
        """
        super(ValidationTab, self).__init__(
            dialog,
            buttons=[("close", "Close"), ("continue", "Continue Submission")]
        )
        self.dialog = dialog
        self.configure_signals()

    def configure_signals(self):
        """Connects button signals to their respective handlers."""
        self.buttons["close"].clicked.connect(self.dialog.on_close)
        self.buttons["continue"].clicked.connect(self.on_continue)

    def populate(self, errors, warnings, infos):
        """
        Populates the tab with validation results, displaying errors, warnings, and infos.

        Args:
            errors (list): List of error messages or objects.
            warnings (list): List of warning messages or objects.
            infos (list): List of informational messages or objects.
        """
        # Organize validation results
        obj = {
            "error": errors,
            "warning": warnings,
            "info": infos
        }
        has_issues = False

        # Add widgets for each validation entry
        for severity in ["error", "warning", "info"]:
            for entry in obj[severity]:
                has_issues = True
                widget = NoticeGrp(entry, severity)
                self.layout.addWidget(widget)

        # Display success message if no issues
        if not has_issues:
            widget = NoticeGrp("No issues found", "success")
            self.layout.addWidget(widget)

        # Align content to the top
        self.layout.addStretch()

        # Disable continue button if errors exist
        self.buttons["continue"].setEnabled(not errors)

    def on_continue(self):
        """
        Handles the 'Continue Submission' button click, initiating job submission.
        """
        logger.debug("Continue Submission...")
        node = self.dialog.node
        use_daemon = node.parm("use_daemon").eval()

        if node:
            # Switch to the progress tab
            self.dialog.show_progress_tab()
            logger.debug("Submitting jobs...")
            # Submit jobs via the progress tab
            self.dialog.progress_tab.submit(node)