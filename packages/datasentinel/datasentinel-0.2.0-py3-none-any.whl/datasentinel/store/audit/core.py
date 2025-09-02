from abc import ABC, abstractmethod
import logging

from datasentinel.core import DataSentinelError
from datasentinel.store.audit.row import BaseAuditRow


class AuditStoreError(DataSentinelError):
    pass


class AuditStoreManagerError(DataSentinelError):
    pass


class AuditStoreAlreadyExistsError(AuditStoreManagerError):
    pass


class AuditStoreNotFoundError(AuditStoreManagerError):
    pass


class AbstractAuditStore(ABC):
    """Base class for all audit store implementations."""

    def __init__(self, name: str, disabled: bool):
        self._disabled = disabled
        self._name = name

    @property
    def name(self) -> str:
        """Return the name of the audit store."""
        return self._name

    @property
    def disabled(self) -> bool:
        """Return whether the audit store is disabled."""
        return self._disabled

    @abstractmethod
    def append(self, row: BaseAuditRow) -> None:
        """Append a row to the audit store.

        Args:
            row: The row to append.
        """


class AbstractAuditStoreManager(ABC):
    """Base class for all audit store manager implementations."""

    @property
    def _logger(self) -> logging.Logger:  # pragma: no cover
        return logging.getLogger(__name__)

    @abstractmethod
    def count(self, enabled_only: bool = False) -> int:
        """Return the number of registered audit stores

        Args:
            enabled_only: Whether to only consider enabled audit stores.

        Returns:
            The number of registered audit stores
        """

    @abstractmethod
    def get(self, name: str) -> AbstractAuditStore:
        """Return the audit store with the given name.

        Args:
            name: The name of the audit store to get.

        Returns:
            The audit store with the given name.

        Raises:
            AuditStoreNotFoundError: If the audit store with the given name is not registered.
        """

    @abstractmethod
    def register(self, audit_store: AbstractAuditStore, replace: bool = False) -> None:
        """Register an audit store.

        Args:
            audit_store: The audit store to register.
            replace: Whether to replace an existing audit store if it already exists.

        Raises:
            AuditStoreAlreadyExistsError: If the audit store with the given name already exists
                and replace is False.
        """

    @abstractmethod
    def remove(self, name: str) -> None:
        """Remove an audit store with the given name.

        Args:
            name: The name of the audit store to remove.

        Raises:
            AuditStoreNotFoundError: If the audit store with the given name is not registered.
        """

    @abstractmethod
    def exists(self, name: str) -> bool:
        """Check if an audit store with the given name exists.

        Args:
            name: The name of the audit store to check.

        Returns:
            True or false whether the audit store with the given name exists.
        """

    @abstractmethod
    def append(self, audit_store: str, row: BaseAuditRow) -> None:
        """Append a row to the audit store with the given name.

        Args:
            audit_store: The audit store to append the row to.
            row: The audit row to append.
        """

    @abstractmethod
    def append_to_all_stores(self, row: BaseAuditRow) -> None:
        """Append a row all the audit stores registered.

        Args:
            row: The audit row to append.
        """
