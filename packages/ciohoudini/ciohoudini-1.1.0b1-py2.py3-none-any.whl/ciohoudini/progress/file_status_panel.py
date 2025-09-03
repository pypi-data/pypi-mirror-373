from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
)

from PySide2.QtCore import Qt, QEvent

from ciohoudini.progress.file_status_row import FileStatusRow


class FileStatusPanel(QWidget):
    def __init__(self, *args, **kwargs):
        super(FileStatusPanel, self).__init__(*args, **kwargs)
        self.auto_scroll = True
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create the QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget(self.scroll_area)
        self.scroll_area.setWidget(scroll_widget)

        # Create a QVBoxLayout for the scroll widget
        self.scroll_layout = QVBoxLayout(scroll_widget)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        layout.addWidget(self.scroll_area)

        # Create a dictionary to hold the status rows
        self.status_rows = {}

    def event(self, event):
        """Kill auto scroll on mouse press"""
        if event.type() == QEvent.MouseButtonPress:
            self.auto_scroll = False
        return super().event(event)

    def focus_activity(self, widget):
        """Scroll to the last widget that's changing."""
        if widget and self.auto_scroll:
            self.scroll_area.ensureWidgetVisible(widget, 10, 10)

    def reset(self):
        """Clear the status rows."""
        for filename in self.status_rows:
            self.status_rows[filename].deleteLater()
        self.status_rows = {}
        self.auto_scroll = True

    def set_progress(self, progress):
        """Update status row based on progress.

        Make elements if they don't exist.
        """
        widget_of_interest = None

        i = 0
        for filename in progress["file_progress"]:


            file_details = progress["file_progress"][filename]
            if filename not in self.status_rows:
                fsr = FileStatusRow(filename)
                self.status_rows[filename] = fsr
                self.scroll_layout.addWidget(fsr)

            self.status_rows[filename].status_chip.update_status(file_details)

            working = (
                file_details["bytes_uploaded"] > 0
                and file_details["bytes_uploaded"] < file_details["bytes_to_upload"]
            )
            if working or i == 0:
                widget_of_interest = self.status_rows[filename]
                
            i +=1

        # Scroll to the widget that's changing
        if widget_of_interest:
            self.focus_activity(widget_of_interest.status_chip)
