# aiko_services will print logs to stdout if AIKO_LOG_MQTT=all or
# register its own logging.StreamHandler if AIKO_LOG_MQTT is unset,
# both causing duplication of logs with the StreamHandler created below
import os

os.environ["AIKO_LOG_MQTT"] = "true"

from .cli import *
from .client import *
from .core import *
from .version import *
