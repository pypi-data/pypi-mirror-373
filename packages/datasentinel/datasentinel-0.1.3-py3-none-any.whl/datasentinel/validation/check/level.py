from enum import Enum


class CheckLevel(Enum):
    """Enum for check severity levels"""

    WARNING = 0
    ERROR = 1
    CRITICAL = 2
