import threading

from datasentinel.store.result.core import (
    AbstractResultStore,
    AbstractResultStoreManager,
    ResultStoreAlreadyExistsError,
    ResultStoreError,
    ResultStoreNotFoundError,
)
from datasentinel.validation.result import DataValidationResult


class ResultStoreManager(AbstractResultStoreManager):
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._result_stores: dict[str, AbstractResultStore] = {}

    def count(self, enabled_only: bool = False) -> int:
        return len(
            [
                store
                for store in self._result_stores.values()
                if not enabled_only or (enabled_only and not store.disabled)
            ]
        )

    def get(self, name: str) -> AbstractResultStore:
        if not self.exists(name):
            raise ResultStoreNotFoundError(f"A result store with name '{name}' does not exist.")
        return self._result_stores[name]

    def register(self, result_store: AbstractResultStore, replace: bool = False) -> None:
        if self.exists(result_store.name) and not replace:
            raise ResultStoreAlreadyExistsError(
                f"A result store with name '{result_store.name}' already exists."
            )
        with self._lock:
            self._result_stores[result_store.name] = result_store

    def remove(self, name: str) -> None:
        if not self.exists(name):
            raise ResultStoreNotFoundError(f"A result store with name '{name}' does not exist.")
        with self._lock:
            del self._result_stores[name]

    def exists(self, name: str) -> bool:
        return name in self._result_stores

    def store_all(self, result_stores: list[str], result: DataValidationResult) -> None:
        for result_store in result_stores:
            self._store(result_store=self.get(result_store), result=result)

    def _store(self, result_store: AbstractResultStore, result: DataValidationResult) -> None:
        if result_store.disabled:
            self._logger.warning(
                f"Result store '{result_store.name}' is disabled, skipping saving results."
            )
            return
        try:
            result_store.store(result=result)
        except ResultStoreError as e:
            self._logger.error(
                f"There was an error while trying to save results "
                f"using result store '{result_store.name}'. Error: {e!s}"
            )
