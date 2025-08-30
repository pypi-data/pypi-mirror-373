from typing import Any

import lazy_loader as lazy


try:
    from .slack_message_renderer import SlackMessageRenderer  # noqa: F401
except (ImportError, RuntimeError):  # pragma: no cover
    SlackMessageRenderer: Any

__getattr__, __dir__, __all__ = lazy.attach(
    __name__,
    submod_attrs={
        "slack_message_renderer": ["SlackMessageRenderer"],
    },
)
