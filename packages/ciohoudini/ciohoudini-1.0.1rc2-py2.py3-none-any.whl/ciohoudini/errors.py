import hou
import traceback
from contextlib import contextmanager

@contextmanager
def show():
    try:
        yield
    except hou.InvalidInput as err:
        hou.ui.displayMessage(
            title="Error",
            text=err.instanceMessage(),
            details_label="Show stack trace",
            details=traceback.format_exc(),
            severity=hou.severityType.ImportantMessage,
        )
    except hou.Error as err:
        hou.ui.displayMessage(
            title="Error",
            text=err.instanceMessage(),
            details_label="Show stack trace",
            details=traceback.format_exc(),
            severity=hou.severityType.Error,
        )

    except (TypeError, ValueError) as err:
        hou.ui.displayMessage(
            title="Error",
            text=str(err),
            details_label="Show stack trace",
            details=traceback.format_exc(),
            severity=hou.severityType.Error,
        )

    except (Exception) as err:
        hou.ui.displayMessage(
            title="Error",
            text=str(err),
            details_label="Show stack trace",
            details=traceback.format_exc(),
            severity=hou.severityType.Error,
        )

