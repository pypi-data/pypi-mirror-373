from typing import Any

import lazy_loader as lazy


try:
    from .database_audit_store import DatabaseAuditStore  # noqa: F401
except (ImportError, RuntimeError):  # pragma: no cover
    DatabaseAuditStore: Any

__getattr__, __dir__, __all__ = lazy.attach(
    __name__,
    submod_attrs={
        "database_audit_store": ["DatabaseAuditStore"],
    },
)
