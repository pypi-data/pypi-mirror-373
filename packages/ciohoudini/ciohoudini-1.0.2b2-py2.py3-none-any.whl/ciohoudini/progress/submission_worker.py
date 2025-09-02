"""
Workers that run in a separate thread.
"""
from ciocore import conductor_submit, exceptions
import sys
import logging
import copy
import traceback


from PySide2.QtCore import QRunnable, QObject, Signal
from PySide2 import QtCore


logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    on_start = Signal(dict)
    on_job_start = Signal(dict)
    on_progress = Signal(dict)
    on_response = Signal(dict)
    on_error = Signal(dict)
    on_done = Signal()


class SubmissionWorkerBase(QRunnable):
    @classmethod
    def create(
        cls,
        submissions,
        job_count,
    ):
        return SubmissionWorker(submissions, job_count)

    def __init__(self):
        """
        Set up common submission worker attributes.
        """
        super().__init__()
        self.signals = WorkerSignals()

        self._is_cancelled = False
        self._raise_exception = False

        self.current_submit_index = 0
        self.current_submit_title = ""

    def progress_handler(self, progress):
        """
        Emit the progress signal.

        Embellish dict with the current job number and title.
        """
        result = self._progress_dict(progress)

        result.update(
            {
                "job_index": self.current_submit_index,
                "job_title": self.current_submit_title,
            }
        )

        self.signals.on_progress.emit(result)

    def error_handler(self, exception_type, exception, tb):
        """
        Emit the error signal.

        Embellish dict with the current job number and title.
        """
        traceback_string = "".join(traceback.format_tb(tb))
        exception_type.__name__

        error = {
            "body": f"\033[31mjob submission failed.\033[0m",  # Red color for error message
            "exception": exception,
            "traceback": traceback_string,
            "exception_type": exception_type.__name__,
            "job_title": self.current_submit_title,
            "status": "error",
            "response_code": 500,
        }

        self.signals.on_error.emit(error)

    def response_handler(self, response, response_code):
        response.update(
            {
                "response_code": response_code,
                "job_title": self.current_submit_title,
            }
        )

        self.signals.on_response.emit(response)

    def cancel(self):
        self._is_cancelled = True

    def raise_exception(self):
        self._raise_exception = True

    def emit_start(self, job_count):
        """Emit the start signal."""
        self.signals.on_start.emit({"job_count": job_count})

    def emit_job_start(self):
        """Emit the job start signal."""
        self.signals.on_job_start.emit(
            {
                "job_index": self.current_submit_index,
                "job_title": self.current_submit_title,
            }
        )

    def emit_done(self):
        """Emit the done signal."""
        self.signals.on_done.emit()

    @staticmethod
    def _progress_dict(progress):
        """Convert upload_stats object to a plain old (JSONifyable) dict."""
        if not hasattr(progress, "files_to_analyze"):
            return {}
        dikt = {
            "files_to_analyze": progress.files_to_analyze or 0,
            "files_to_upload": progress.files_to_upload or 0,
            "bytes_to_upload": progress.bytes_to_upload.value,
            "bytes_uploaded": progress.bytes_uploaded.value,
            "transfer_rate": progress.transfer_rate.value or 0,
            "file_progress": copy.deepcopy(progress.file_progress.value),
        }

        if progress.percent_complete.value:
            dikt["percent_complete"] = progress.percent_complete.value * 100.0
        else:
            dikt["percent_complete"] = 0

        if progress.time_remaining and progress.time_remaining.value:
            dikt["time_remaining"] = progress.time_remaining.value.total_seconds()
        if progress.elapsed_time:
            dikt["elapsed_time"] = progress.elapsed_time.total_seconds()

        if dikt["files_to_analyze"] > 0:
            dikt["processed_md5s"] = len(
                [f["md5"] for f in dikt["file_progress"].values() if f["md5"]]
            )
            dikt["md5_percent"] = (dikt["processed_md5s"] * 100.0) / dikt[
                "files_to_analyze"
            ]
        else:
            dikt["md5_percent"] = 100
        return dikt


class SubmissionWorker(SubmissionWorkerBase):
    """The worker that submits jobs to Conductor."""

    def __init__(self, submissions, job_count):
        super(SubmissionWorker, self).__init__()
        self.current_submit_function = None
        self.submissions = submissions
        self.job_count = job_count

    def run(self):
        i = 0
        self.emit_start(self.job_count)
        for submission in self.submissions:
            self.current_submit_index = i
            self.current_submit_title = submission["job_title"]
            self.emit_job_start()

            try:
                self.current_submit_function = conductor_submit.Submit(submission)
                self.current_submit_function.progress_handler = self.progress_handler
                response, responseCode = self.current_submit_function.main()
            except exceptions.UserCanceledError:
                self.error_handler(*sys.exc_info())
                break
            except Exception:
                self.error_handler(*sys.exc_info())
                continue

            self.response_handler(response, responseCode)
            # QtCore.QCoreApplication.processEvents()
            i += 1

        self.emit_done()

    def cancel(self):
        super(SubmissionWorker, self).cancel()
        if self.current_submit_function:
            self.current_submit_function.stop_work()

