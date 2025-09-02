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
    background-color: {k.MD5_GRADIENT};
}}
"""


class MD5ProgressWidget(ProgressWidgetBase):
    """
    Show the progress of the MD5 calculation phase.
    """

    LABEL = "Computing MD5"

    def __init__(self, *args, **kwargs):
        super(MD5ProgressWidget, self).__init__(*args, **kwargs)
        self.progress_bar.setStyleSheet(PROGRESS_BAR_STYLESHEET)

    def set_progress(self, progress):
        numerator = progress["processed_md5s"]
        denominator = progress["files_to_analyze"]
        label = f"{self.LABEL}: {numerator}/{denominator}"
        percentage = numerator / denominator * 100
        super(MD5ProgressWidget, self).set_progress(percentage, label)
