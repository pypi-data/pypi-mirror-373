"""`datasentinel.notification.notifier.email` contains all email notifiers."""

from typing import Any

import lazy_loader as lazy


try:
    from .smtp_email_notifier import SMTPEmailNotifier  # noqa: F401
except (ImportError, RuntimeError):  # pragma: no cover
    SMTPEmailNotifier: Any

__getattr__, __dir__, __all__ = lazy.attach(
    __name__,
    submod_attrs={
        "smtp_email_notifier": ["SMTPEmailNotifier"],
    },
)
