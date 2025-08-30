import json
from typing import Any

from pyspark.sql import DataFrame

from datasentinel.validation.failed_rows_dataset.core import (
    AbstractFailedRowsDataset,
    FailedRowsDatasetError,
)


class SparkFailedRowsDataset(AbstractFailedRowsDataset[DataFrame]):
    def __init__(self, data: DataFrame):
        super().__init__(data)

    @property
    def data(self) -> DataFrame:
        return self._data

    def count(self) -> int:
        return self._data.count()

    def to_dict(self, limit: int | None = None) -> list[dict[str, Any]]:
        if limit is not None and not limit > 0:
            raise FailedRowsDatasetError("Limit must be greater than 0")

        data = self._data.limit(limit) if limit is not None else self._data
        return [row.asDict() for row in data.toLocalIterator()]

    def to_json(self, limit: int | None = None) -> str:
        return json.dumps(self.to_dict(limit))
