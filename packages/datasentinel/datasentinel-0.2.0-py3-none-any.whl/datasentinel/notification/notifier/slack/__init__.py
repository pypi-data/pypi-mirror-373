"""`datasentinel.notification.notifier.slack` contains Slack notifier implementations."""

from typing import Any

import lazy_loader as lazy


try:
    from .slack_notifier import SlackNotifier  # noqa: F401
except (ImportError, RuntimeError):  # pragma: no cover
    SlackNotifier: Any

__getattr__, __dir__, __all__ = lazy.attach(
    __name__,
    submod_attrs={
        "slack_notifier": ["SlackNotifier"],
    },
)
