import re

from enum import Enum

SCENARIO_LABEL_NAME_PATTERN = re.compile(r"^scenarios\.ai\.sap\.com/[\w.-]+$")

DEBUG_ENV_VAR_NAME = "DEBUG"

class Timeouts(Enum):
    READ_TIMEOUT = 60
    CONNECT_TIMEOUT = 60
    NUM_REQUEST_RETRIES = 3
