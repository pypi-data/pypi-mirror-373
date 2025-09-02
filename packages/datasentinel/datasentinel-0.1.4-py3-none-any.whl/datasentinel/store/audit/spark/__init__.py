from typing import Any

import lazy_loader as lazy


try:
    from .deltatable_audit_store import DeltaTableAuditStore  # noqa: F401
except (ImportError, RuntimeError):  # pragma: no cover
    DeltaTableAuditStore: Any

__getattr__, __dir__, __all__ = lazy.attach(
    __name__,
    submod_attrs={
        "deltatable_audit_store": ["DeltaTableAuditStore"],
    },
)
