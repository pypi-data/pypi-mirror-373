from enum import Enum


# TODO I think enum values should be in uppercase
class LogMessageSeverity(Enum):
    DEBUG = 100
    VERBOSE = 200
    INIT = 300
    INFO = 500
    WARNING = 600
    ERROR = 700
    CRITICAL = 800
    EXCEPTION = 900


class StartEndEnum(Enum):
    START = 400
    END = 402
