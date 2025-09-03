from ciohoudini.progress.progress_widget_base import ProgressWidgetBase
from ciohoudini import const as k

PROGRESS_BAR_STYLESHEET = f"""
QProgressBar {{
    border: 1px solid {k.OFF_COLOR_DARK};
    border-radius: 3px;
}}
QProgressBar::chunk {{
    width: 4px;
    margin:2px;
    background-color: {k.UPLOAD_GRADIENT};
}}
"""


class UploadProgressWidget(ProgressWidgetBase):
    """
    Show progress on the upload process of job submission.
    """
    LABEL = "File Upload"
    def __init__(self, *args, **kwargs):
        super(UploadProgressWidget, self).__init__(*args, **kwargs )
        self.progress_bar.setStyleSheet(PROGRESS_BAR_STYLESHEET)

    def set_progress(self, progress):
        super(UploadProgressWidget, self).set_progress(progress["percent_complete"])

