import threading

from datasentinel.store.audit.core import (
    AbstractAuditStore,
    AbstractAuditStoreManager,
    AuditStoreAlreadyExistsError,
    AuditStoreError,
    AuditStoreNotFoundError,
)
from datasentinel.store.audit.row import BaseAuditRow


class AuditStoreManager(AbstractAuditStoreManager):
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._audit_stores: dict[str, AbstractAuditStore] = {}

    def count(self, enabled_only: bool = False) -> int:
        return len(
            [
                store
                for store in self._audit_stores.values()
                if not enabled_only or (enabled_only and not store.disabled)
            ]
        )

    def get(self, name: str) -> AbstractAuditStore:
        if not self.exists(name):
            raise AuditStoreNotFoundError(f"An audit store with '{name}' does not exist.")
        return self._audit_stores[name]

    def register(self, audit_store: AbstractAuditStore, replace: bool = False) -> None:
        if self.exists(audit_store.name) and not replace:
            raise AuditStoreAlreadyExistsError(
                f"An audit store with name '{audit_store.name}' already exists."
            )
        with self._lock:
            self._audit_stores[audit_store.name] = audit_store

    def remove(self, name: str) -> None:
        if not self.exists(name):
            raise AuditStoreNotFoundError(f"An audit store with name '{name}' does not exist.")
        with self._lock:
            del self._audit_stores[name]

    def exists(self, name: str) -> bool:
        return name in self._audit_stores

    def append(self, audit_store: str, row: BaseAuditRow) -> None:
        self._append(self.get(audit_store), row)

    def append_to_all_stores(self, row: BaseAuditRow) -> None:
        for audit_store in self._audit_stores.values():
            self._append(audit_store, row)

    def _append(
        self,
        audit_store: AbstractAuditStore,
        row: BaseAuditRow,
    ) -> None:
        if audit_store.disabled:
            self._logger.warning(
                f"Audit store '{audit_store.name}' is disabled, skipping appending audit row."
            )
            return
        try:
            audit_store.append(row=row)
        except AuditStoreError as e:
            self._logger.error(
                f"There was an error while trying to append row "
                f"to audit store '{audit_store.name}'. Error: {e!s}"
            )
