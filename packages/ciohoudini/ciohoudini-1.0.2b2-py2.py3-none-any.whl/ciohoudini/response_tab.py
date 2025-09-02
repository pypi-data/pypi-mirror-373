from ciohoudini.components.notice_grp import NoticeGrp
from ciohoudini.components.buttoned_scroll_panel import ButtonedScrollPanel

from ciocore import config
import urllib.parse

CONFIG = config.get()

try:
    import ciocore.loggeria
    logger = ciocore.loggeria.get_conductor_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Failed to import ciocore.loggeria; using default logger.")

class ResponseTab(ButtonedScrollPanel):
    """A tab for displaying job submission responses in a scrollable panel with a close button.

    Inherits from ButtonedScrollPanel to provide a scrollable area with predefined buttons.
    Displays responses with appropriate severity, messages, URLs, and error details.
    """

    def __init__(self, dialog):
        """Initialize the ResponseTab with a dialog and close button.

        Args:
            dialog: The parent dialog object that contains this tab.
        """
        super(ResponseTab, self).__init__(dialog, buttons=[("close", "Close")])
        self.dialog = dialog
        self.configure_signals()

    def configure_signals(self):
        """Connect the close button's clicked signal to the dialog's on_close slot."""
        self.buttons["close"].clicked.connect(self.dialog.on_close)

    def hydrate(self, responses):
        """Populate the tab with job submission responses.

        Clears existing widgets and adds new NoticeGrp widgets for each response.
        Each widget displays a message, severity, optional URL, and error details.

        Args:
            responses: List of response dictionaries, each containing:
                - Success response:
                    - body: Response message (str)
                    - jobid: Job identifier (str)
                    - status: "success" (str)
                    - uri: API endpoint for the job (str)
                    - job_title: Title of the job (str)
                    - response_code: HTTP status code (int)
                - Error response:
                    - body: Error message (str)
                    - exception: Exception message (str)
                    - traceback: Exception traceback (str)
                    - exception_type: Type of exception (str)
                    - job_title: Title of the job (str)
                    - status: "error" (str)
                    - response_code: HTTP status code (int)
        """
        logger.debug("Showing responses...")
        self.clear()  # Remove existing widgets from the layout
        for res in responses:
            severity = self._get_severity(res)  # Determine the severity level
            message = self._get_message(res)    # Construct the display message
            url = self._get_url(res)            # Get optional dashboard URL
            details = self._get_details(res)    # Get error details if applicable

            # Create and add a NoticeGrp widget to the layout
            widget = NoticeGrp(message, severity=severity, url=url, details=details)
            self.layout.addWidget(widget)
        self.layout.addStretch()  # Add stretch to push widgets to the top
        logger.debug("Showing responses is complete.")

    @staticmethod
    def _get_severity(response):
        """Determine the severity level for a response.

        Args:
            response: Dictionary containing response data.

        Returns:
            str: Severity level ("success", "error", or "warning").
        """
        status = response["status"]
        # Treat UserCanceledError as a warning instead of an error
        if response["status"] == "error" and response["exception_type"] == "UserCanceledError":
            status = "warning"
        return status

    @staticmethod
    def _get_message(response):
        """Construct the display message for a response.

        Combines body, exception type, job title, and job ID into a single string.

        Args:
            response: Dictionary containing response data.

        Returns:
            str: Formatted message string.
        """
        message = response["body"].capitalize().strip(".")
        if "exception_type" in response:
            message += " - {}".format(response["exception_type"])
        if "job_title" in response:
            message += " - {}".format(response["job_title"])
        jobid = "jobid" in response and response["jobid"]
        if jobid:
            message += " ({})".format(jobid)
        return message

    @staticmethod
    def _get_url(response):
        """Generate a dashboard URL for successful responses.

        Args:
            response: Dictionary containing response data.

        Returns:
            tuple or None: A tuple of (label, URL) for successful responses, else None.
        """
        widget_url = None
        if response["status"] == "success" and response["uri"]:
            label = "Go to dashboard"
            # Construct the full URL by joining base URL with modified URI
            url = urllib.parse.urljoin(
                CONFIG["url"], response["uri"].replace("jobs", "job")
            )
            widget_url = (label, url)
        return widget_url

    @staticmethod
    def _get_details(response):
        """Extract error details for error responses.

        Args:
            response: Dictionary containing response data.

        Returns:
            str or None: Formatted error details string, or None if not applicable.
        """
        if not response["status"] == "error":
            return
        if not ("exception_type" in response and "traceback" in response and "exception" in response):
            return
        ex_type = response["exception_type"]
        ex_msg = response["exception"]
        ex_trace = response["traceback"]
        return f"{ex_type}: {ex_msg}\nTraceback:\n{ex_trace}"

    def on_close_button(self):
        """Handle the close button click event.

        Calls the dialog's on_close method to close the dialog.
        """
        self.dialog.on_close()