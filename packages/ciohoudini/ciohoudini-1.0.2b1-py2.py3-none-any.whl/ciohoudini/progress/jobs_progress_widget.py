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
    background-color: {k.JOBS_GRADIENT};
}}
"""


class JobsProgressWidget(ProgressWidgetBase):
    """
    Show the progress of the batch of jobs.
    """

    LABEL = "Jobs Progress"

    def __init__(self, *args, **kwargs):
        super(JobsProgressWidget, self).__init__(*args, **kwargs)
        self.progress_bar.setStyleSheet(PROGRESS_BAR_STYLESHEET)

    def set_job_count(self, count):
        self.job_count = count

    def reset(self, start_event=None):
        super(JobsProgressWidget, self).reset()
        if start_event:
            self.set_job_count(start_event["job_count"])

    def set_progress(self, progress):
        title = progress["job_title"]
        numerator = progress["job_index"]

        denominator = self.job_count

        label = f"{self.LABEL}: {numerator+1}/{denominator} - {title}"

        total_percentage = int(((numerator + 1) / denominator) * 100) if denominator > 0 else 0


        super(JobsProgressWidget, self).set_progress(total_percentage, label)
