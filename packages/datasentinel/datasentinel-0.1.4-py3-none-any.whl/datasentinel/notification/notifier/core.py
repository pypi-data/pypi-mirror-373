"""Core components for creating and managing notifiers."""

from abc import ABC, abstractmethod
import logging

from datasentinel.core import DataSentinelError
from datasentinel.validation.core import NotifyOnEvent
from datasentinel.validation.result import DataValidationResult


class NotifierError(DataSentinelError):
    """Base exception for notifier-related errors."""

    pass


class NotifierManagerError(DataSentinelError):
    """Base exception for notifier manager-related errors."""

    pass


class NotifierAlreadyExistsError(NotifierManagerError):
    """Raised when attempting to register an already existing notifier."""

    pass


class NotifierNotFoundError(NotifierManagerError):
    """Raised when a requested notifier is not found."""

    pass


class AbstractNotifier(ABC):
    """Abstract base class for notifiers."""

    def __init__(self, name, disabled=False):
        """Initializes the AbstractNotifier.

        Args:
            name: The name of the notifier.
            disabled: Whether the notifier is disabled.
        """
        self._name = name
        self._disabled = disabled

    @property
    def name(self):
        """Gets the name of the notifier."""
        return self._name

    @property
    def disabled(self):
        """Checks if the notifier is disabled."""
        return self._disabled

    @property
    def _logger(self):  # pragma: no cover
        return logging.getLogger(__name__)

    @abstractmethod
    def notify(self, result):
        """Sends a notification based on the data validation result.

        Args:
            result: The data validation result to notify.
        """


class AbstractNotifierManager(ABC):
    """Abstract base class for notifier managers."""

    @property
    def _logger(self):
        return logging.getLogger(__name__)

    @abstractmethod
    def count(self, enabled_only=False) -> int:
        """Return the number of registered notifiers.

        Args:
            enabled_only: Whether to only consider enabled notifiers.

        Returns:
            The number of registered notifiers.
        """

    @abstractmethod
    def get(self, name) -> AbstractNotifier:
        """Get notifier by name.

        Args:
            name: Notifier name.

        Returns:
            Notifier instance with the given name.
        """

    @abstractmethod
    def register(self, notifier: AbstractNotifier, replace: bool = False) -> None:
        """Register notifier.

        Args:
            notifier: Notifier to register.
            replace: Whether to replace an existing notifier if it already exists.

        Raises:
            NotifierAlreadyExistsError: When the notifier already exists and replace is False.
        """

    @abstractmethod
    def remove(self, name) -> None:
        """Remove notifier by name.

        Args:
            name: Name of the notifier to be removed.

        Raises:
            NotifierNotFoundError: When a notifier with the given name was not registered before.
        """

    @abstractmethod
    def exists(self, name) -> bool:
        """Check if notifier exists.

        Args:
            name: Name of the notifier to check if its registered.

        Returns:
            Whether the notifier exists.
        """

    @abstractmethod
    def notify_all_by_event(
        self,
        notifiers_by_events: dict[NotifyOnEvent, list[str]],
        result: DataValidationResult,
    ):
        """Notify a validation node result using the specified notifiers for each event.

        Args:
            notifiers_by_events: A dictionary where each key is
                an event, and the corresponding value is a list of the notifiers name to be used
                when that event occurs.
            result: The validation node result to be notified.
        """
