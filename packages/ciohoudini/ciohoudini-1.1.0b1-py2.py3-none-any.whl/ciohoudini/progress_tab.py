"""
Module for managing the progress tab UI in the Conductor plugin for Houdini.

This module defines a PySide2-based widget that displays the progress of job submissions,
including job batch progress, MD5 generation, file uploads, and file status details.
"""

from ciohoudini import payload, submit, rops
from ciohoudini.components.buttoned_scroll_panel import ButtonedScrollPanel

from ciohoudini.progress.md5_progress_widget import MD5ProgressWidget
from ciohoudini.progress.upload_progress_widget import UploadProgressWidget
from ciohoudini.progress.jobs_progress_widget import JobsProgressWidget

from ciohoudini.progress.file_status_panel import FileStatusPanel
from ciohoudini.progress.submission_worker import SubmissionWorker, SubmissionWorkerBase

import logging

from PySide2.QtCore import Qt
import threading
import time

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")


class ProgressTab(ButtonedScrollPanel):
    """
    A PySide2 widget for displaying job submission progress in the Conductor plugin.

    Displays four progress elements: job batch progress, MD5 generation, file uploads,
    and detailed file status. Manages submission workers and handles responses.

    Attributes:
        dialog: Parent dialog containing the tab.
        progress_list (list): List to track progress (currently unused).
        responses (list): List of submission responses or errors.
        submissions (list): List of submission payloads.
        worker: Submission worker instance for processing jobs.
        worker_thread: Thread for running the submission worker.
        jobs_widget: Widget for job batch progress.
        md5_widget: Widget for MD5 generation progress.
        upload_widget: Widget for upload progress.
        file_status_panel: Widget for detailed file status.
    """

    def __init__(self, dialog):
        """
        Initialize the progress tab widget.

        Args:
            dialog: Parent dialog containing the progress tab.
        """
        # Initialize parent class with a cancel button
        super(ProgressTab, self).__init__(
            dialog, buttons=[("cancel", "Cancel")]
        )
        self.dialog = dialog
        self.progress_list = []
        self.responses = []
        self.submissions = []
        self.worker = None
        self.worker_thread = None

        # Initialize progress widgets
        self.jobs_widget = JobsProgressWidget()
        self.md5_widget = MD5ProgressWidget()
        self.upload_widget = UploadProgressWidget()
        self.file_status_panel = FileStatusPanel()

        # Add widgets to layout
        self.layout.addWidget(self.jobs_widget)
        self.layout.addWidget(self.md5_widget)
        self.layout.addWidget(self.upload_widget)
        self.layout.addWidget(self.file_status_panel)

        # Connect cancel button to handler
        self.buttons["cancel"].clicked.connect(self.on_cancel_button)


    def get_submission_payload(self, node):
        """
        Retrieve the submission payload for a given node.

        Handles both generator nodes (using precomputed payloads) and other nodes
        (resolving payloads with asset scanning).

        The Generator node includes a Selection tab where users choose which Solaris nodes to submit;
        their choices are saved as payloads for later. From there, users proceed to the Validation tab and then to Progress,
        where we consume the stored Generator payloads. Alternatively, we could record just the names of the selected Solaris
        nodes instead of the full payloads.

        For all other nodes (which lack a Selection tab), the workflow skips straight to Validation,
        and in Progress we build the submission payload on demand.

        Args:
            node: Conductor Submitter node to generate payload for.

        Returns:
            list: List of submission payload dictionaries.
        """
        # Use precomputed payloads for generator nodes
        if self.dialog.is_generation_node(node):
            submission_payload = self.dialog.payloads
        else:
            if self.dialog.payloads:
                submission_payload = self.dialog.payloads
            else:
                # Configure kwargs for full payload resolution
                kwargs = {}
                kwargs["do_asset_scan"] = True
                kwargs["task_limit"] = -1
                submission_payload = payload.resolve_payloads(node, **kwargs)
        return submission_payload


    def submit(self, node):
        """
        Submit jobs for processing.

        Initializes progress widgets, retrieves submission payloads, and starts a worker
        thread to process submissions.

        Args:
            node: Conductor Submitter node to submit jobs for.
        """
        # Reset progress widgets
        self.jobs_widget.reset()
        self.md5_widget.reset()
        self.upload_widget.reset()
        self.file_status_panel.reset()

        # Clear previous responses
        self.responses = []

        # Get submission payloads
        self.submissions = self.get_submission_payload(node)

        # Log if no submissions are found
        if not self.submissions:
            logger.info("No submissions found")
            return

        # Create and configure submission worker
        job_count = len(self.submissions)
        self.worker = SubmissionWorkerBase.create(self.submissions, job_count)

        # Connect worker signals
        self.connect_worker_signals()

        # Start worker in a separate thread
        self.worker_thread = threading.Thread(target=self.start_worker)
        self.worker_thread.start()


    def start_worker(self):
        """
        Run the submission worker in its thread.
        """
        self.worker.run()

    def connect_worker_signals(self):
        """
        Connect worker signals to progress widget slots.

        Links worker events (start, progress, response, done, error) to appropriate
        UI updates.
        """
        # Connect signals to reset widgets on job start
        self.worker.signals.on_start.connect(self.jobs_widget.reset, Qt.QueuedConnection)
        self.worker.signals.on_job_start.connect(self.md5_widget.reset, Qt.QueuedConnection)
        self.worker.signals.on_job_start.connect(self.upload_widget.reset, Qt.QueuedConnection)
        # Connect progress updates
        self.worker.signals.on_progress.connect(self.md5_widget.set_progress, Qt.QueuedConnection)
        self.worker.signals.on_progress.connect(self.upload_widget.set_progress, Qt.QueuedConnection)
        self.worker.signals.on_progress.connect(self.jobs_widget.set_progress, Qt.QueuedConnection)
        self.worker.signals.on_progress.connect(self.file_status_panel.set_progress, Qt.QueuedConnection)
        # Connect response and completion handlers
        self.worker.signals.on_response.connect(self.handle_response, Qt.QueuedConnection)
        self.worker.signals.on_done.connect(self.handle_done, Qt.QueuedConnection)
        self.worker.signals.on_error.connect(self.handle_error, Qt.QueuedConnection)


    def handle_response(self, response):
        """
        Handle a submission response.

        Appends the response to the responses list for later display.

        Args:
            response: Submission response data.
        """
        self.responses.append(response)


    def handle_error(self, error):
        """
        Handle an error during submission.

        Appends the error to the responses list for later display.

        Args:
            error: Error data or message.
        """
        self.responses.append(error)


    def on_cancel_button(self):
        """
        Handle the cancel button click.

        Cancels the submission worker and closes the dialog.
        """
        if self.worker:
            self.worker.cancel()
        self.dialog.on_close()


    def handle_done(self):
        """
        Handle completion of all submissions.

        Updates the UI to show the response tab and displays submission responses.
        """
        logger.debug("Jobs are completed...")

        # Switch to response tab and disable other tabs
        self.dialog.show_response_tab()

        logger.debug("Showing the response ...")
        # Populate response tab with submission responses
        self.dialog.response_tab.hydrate(self.responses)