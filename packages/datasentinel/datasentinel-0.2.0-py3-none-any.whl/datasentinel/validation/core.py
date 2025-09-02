from enum import Enum


class NotifyOnEvent(Enum):
    """Enum for notification trigger events on a data validation process.

    Attributes:
        FAIL: Send notification when a data validation process fails.
        PASS: Send notification when a data validation process passes.
        ALL: Always send notification regardless of the data validation process result status.
    """

    FAIL = "FAIL"
    PASS = "PASS"  # noqa: S105
    ALL = "ALL"
