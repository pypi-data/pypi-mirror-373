from ciohoudini import (
    notice_grp,
    submission_dialog,
    buttoned_scroll_panel,
    validation_tab,
    progress_tab,
    response_tab,
    driver,
    instances,
    miscellaneous,
    project,
    software,
    job_title,
    payload,
    controller,
    takes,
    environment,
    frames,
    errors,
    task,
    context,
    assets,
    submit,
    payload,
    validation,
)

import importlib


def reload():
    """Reload all the modules."""
    for module in [
        notice_grp,
        submission_dialog,
        buttoned_scroll_panel,
        validation_tab,
        progress_tab,
        response_tab,
        validation,
        instances,
        project,
        software,
        takes,
        driver,
        job_title,
        payload,
        controller,
        environment,
        frames,
        errors,
        task,
        context,
        assets,
        miscellaneous,
        submit,
        payload,
    ]:
        importlib.reload(module)
