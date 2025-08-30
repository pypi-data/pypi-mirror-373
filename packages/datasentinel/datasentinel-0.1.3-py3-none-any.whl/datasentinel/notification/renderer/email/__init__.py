from typing import Any

import lazy_loader as lazy


try:
    from .template_email_message_renderer import TemplateEmailMessageRenderer  # noqa: F401
except (ImportError, RuntimeError):  # pragma: no cover
    TemplateEmailMessageRenderer: Any

__getattr__, __dir__, __all__ = lazy.attach(
    __name__,
    submod_attrs={
        "template_email_message_renderer": ["TemplateEmailMessageRenderer"],
    },
)
