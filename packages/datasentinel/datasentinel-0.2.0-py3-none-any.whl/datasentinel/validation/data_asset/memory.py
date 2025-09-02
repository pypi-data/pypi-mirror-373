from typing import Any

from datasentinel.validation.data_asset.core import AbstractDataAsset, DataAssetError


class MemoryDataAsset(AbstractDataAsset[Any]):
    def __init__(self, data: Any, name: str, schema: str | None = None):
        self._data = data
        super().__init__(name=name, schema=schema)

    def load(self) -> Any:
        if self._data is None:
            raise DataAssetError("Data for MemoryDataAsset has not been saved yet.")
        return self._data
