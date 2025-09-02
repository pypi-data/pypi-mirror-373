from typing import Any

import lazy_loader as lazy


try:
    from .deltatable_result_store import DeltaTableResultStore  # noqa: F401
except (ImportError, RuntimeError):  # pragma: no cover
    DeltaTableResultStore: Any

__getattr__, __dir__, __all__ = lazy.attach(
    __name__,
    submod_attrs={
        "deltatable_result_store": ["DeltaTableResultStore"],
    },
)
