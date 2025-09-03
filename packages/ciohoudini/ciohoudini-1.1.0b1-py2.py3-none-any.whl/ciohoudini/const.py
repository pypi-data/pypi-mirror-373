import os


VERSION = "7.4"
PLUGIN_DIR = os.path.dirname(__file__)
try:
    with open(os.path.join(PLUGIN_DIR, "VERSION")) as version_file:
        VERSION = version_file.read().strip()
except BaseException:
    pass


IS_DEV = os.environ.get("CIO_FEATURE_DEV", False)
ENABLE_MOCKS = os.environ.get("CIO_FEATURE_MOCK", False)
FIXTURES_DIR = os.path.expanduser(os.path.join("~", "conductor_fixtures"))

MAX_TASKS = 1000

NOT_CONNECTED = "NOT CONNECTED"
NOT_SAVED = "UNTITLED"

CONDUCTOR_RENDER_NODE_TYPE = "ConductorRender"
CONDUCTOR_RENDER_NODE_NAME = "ConductorRender"

CONFIGURATION_TAB_INDEX = 0
PREVIEW_TAB_INDEX = 1
VALIDATION_TAB_INDEX = 2
PROGRESS_TAB_INDEX = 3
RESPONSE_TAB_INDEX = 4

TAB_NAMES = [
    "Configure",
    "Preview",
    "Validation",
    "Progress",
    "Response",
]


JOBS_COLOR = "#553198"
JOBS_COLOR_DARK = "#392165"
JOBS_GRADIENT = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {JOBS_COLOR_DARK},  stop: 0.3 {JOBS_COLOR},  stop: 0.7 {JOBS_COLOR}, stop:1 {JOBS_COLOR_DARK})"

MD5_COLOR = "#3e36cf"
MD5_COLOR_DARK = "#2e2e7f"
MD5_GRADIENT = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {MD5_COLOR_DARK},  stop: 0.3 {MD5_COLOR},  stop: 0.7 {MD5_COLOR}, stop:1 {MD5_COLOR_DARK})"

UPLOAD_COLOR = "#2b7418"
UPLOAD_COLOR_DARK = "#1c4910"
UPLOAD_GRADIENT = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {UPLOAD_COLOR_DARK},  stop: 0.3 {UPLOAD_COLOR},  stop: 0.7 {UPLOAD_COLOR}, stop:1 {UPLOAD_COLOR_DARK})"

MD5_CACHE_COLOR = "#553198"
MD5_CACHE_COLOR_DARK = "#392165"
MD5_CACHE_GRADIENT = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {MD5_CACHE_COLOR_DARK},  stop: 0.3 {MD5_CACHE_COLOR},  stop: 0.7 {MD5_CACHE_COLOR}, stop:1 {MD5_CACHE_COLOR_DARK})"

UPLOAD_CACHE_COLOR = "#7C45C4"
UPLOAD_CACHE_COLOR_DARK = "#553198"
UPLOAD_CACHE_GRADIENT = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {UPLOAD_CACHE_COLOR_DARK},  stop: 0.3 {UPLOAD_CACHE_COLOR},  stop: 0.7 {UPLOAD_CACHE_COLOR}, stop:1 {MD5_CACHE_COLOR_DARK})"

OFF_COLOR = "#555"
OFF_COLOR_DARK = "#373737"
OFF_GRADIENT = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {OFF_COLOR_DARK},  stop: 0.3 {OFF_COLOR},  stop: 0.7 {OFF_COLOR}, stop:1 {OFF_COLOR_DARK})"
