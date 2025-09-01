from enum import Enum, auto

class LogLevel(Enum):
    """
    **Enums used for logging.**
    """
    INFO = auto()
    WARN = auto()
    ERROR = auto()
    DEBUG = auto()