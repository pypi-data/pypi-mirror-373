# import datetime
import hou

TASK_DEFAULTS = {"first":1, "last":1, "step":1}

def set_for_task(**kwargs):
    """Sets the task context for the current frame.
    """
    for key in TASK_DEFAULTS:
        value = kwargs.get(key, TASK_DEFAULTS[key])
        token = "CIO{}".format(key.upper()) 
        hou.putenv(token, str(value))
        
