"""`NotifierManager` manages all the registered notifiers."""

import threading

from datasentinel.notification.notifier.core import (
    AbstractNotifier,
    AbstractNotifierManager,
    NotifierAlreadyExistsError,
    NotifierError,
    NotifierNotFoundError,
)
from datasentinel.notification.renderer.core import RendererError
from datasentinel.validation.core import NotifyOnEvent
from datasentinel.validation.result import DataValidationResult
from datasentinel.validation.status import Status


class NotifierManager(AbstractNotifierManager):
    """A central place to register and manage notifiers."""

    _lock = threading.Lock()

    def __init__(self) -> None:
        """Initializes the NotifierManager to manage notifiers."""
        self._notifiers: dict[str, AbstractNotifier] = {}

    def count(self, enabled_only: bool = False) -> int:
        """Return the number of registered notifiers, optionally filtered by enabled status."""
        return len(
            [
                notifier
                for notifier in self._notifiers.values()
                if not enabled_only or (enabled_only and not notifier.disabled)
            ]
        )

    def get(self, name: str) -> AbstractNotifier:
        """Get notifier by name.

        Args:
            name: Notifier name.

        Returns:
            Notifier instance with the given name.
        """
        if not self.exists(name):
            raise NotifierNotFoundError(f"Notifier '{name}' does not exist.")
        return self._notifiers[name]

    def register(self, notifier: AbstractNotifier, replace: bool = False) -> None:
        """Register notifier.

        Args:
            notifier: Notifier to register.
            replace: Whether to replace an existing notifier if it already exists.

        Raises:
            NotifierAlreadyExistsError: When the notifier already exists and replace is False.
        """
        if notifier.name in self._notifiers and not replace:
            raise NotifierAlreadyExistsError(
                f"Notifier with name '{notifier.name}' already exists."
            )
        with self._lock:
            self._notifiers[notifier.name] = notifier

    def remove(self, name: str) -> None:
        if not self.exists(name):
            raise NotifierNotFoundError(f"Notifier '{name}' does not exist.")
        with self._lock:
            del self._notifiers[name]

    def exists(self, name: str) -> bool:
        return name in self._notifiers

    def notify_all_by_event(
        self,
        notifiers_by_events: dict[NotifyOnEvent, list[str]],
        result: DataValidationResult,
    ) -> None:
        status = result.status
        notifiers = []
        if status == Status.PASS:
            notifiers.extend(notifiers_by_events.get(NotifyOnEvent.PASS, []))
        else:
            notifiers.extend(notifiers_by_events.get(NotifyOnEvent.FAIL, []))

        notifiers.extend(notifiers_by_events.get(NotifyOnEvent.ALL, []))

        for notifier in notifiers:
            self._notify(notifier=self.get(notifier), result=result)

    def _notify(self, notifier: AbstractNotifier, result: DataValidationResult) -> None:
        if notifier.disabled:
            self._logger.warning(
                f"Notifier '{notifier.name}' is disabled, skipping sending notification."
            )
            return
        try:
            notifier.notify(result=result)
        except (NotifierError, RendererError) as e:
            self._logger.error(
                f"There was an error while trying to send notification "
                f"using notifier '{notifier.name}'. Error: {e!s}"
            )
