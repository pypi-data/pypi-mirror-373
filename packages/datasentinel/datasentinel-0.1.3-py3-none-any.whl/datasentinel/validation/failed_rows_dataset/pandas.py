from typing import Any

from pandas import DataFrame

from datasentinel.validation.failed_rows_dataset.core import (
    AbstractFailedRowsDataset,
    FailedRowsDatasetError,
)


class PandasFailedRowsDataset(AbstractFailedRowsDataset[DataFrame]):
    def __init__(self, data: DataFrame):
        super().__init__(data)

    @property
    def data(self) -> DataFrame:
        return self._data

    def count(self) -> int:
        return self._data.shape[0]

    def to_dict(self, limit: int | None = None) -> list[dict[str, Any]]:
        return self._apply_limit(limit).to_dict(orient="records")

    def to_json(self, limit: int | None = None) -> str:
        return self._apply_limit(limit).to_json(orient="records")

    def _apply_limit(self, limit: int | None) -> DataFrame:
        if limit is not None and not limit > 0:
            raise FailedRowsDatasetError("Limit must be greater than 0")

        return self._data.head(limit) if limit is not None else self._data
