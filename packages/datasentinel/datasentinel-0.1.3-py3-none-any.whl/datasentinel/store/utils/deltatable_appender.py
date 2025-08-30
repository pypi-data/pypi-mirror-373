from copy import deepcopy
from typing import Any, Literal

from delta import DeltaTable
from pyspark.errors import AnalysisException
from pyspark.sql import DataFrame

from datasentinel.core import DataSentinelError
from datasentinel.store.utils.spark_utils import get_spark


class DeltaTableAppenderError(DataSentinelError):
    pass


class DeltaTableAppender:
    def __init__(
        self,
        table: str,
        schema: str,
        dataset_type: Literal["file", "table"],
        external_path: str | None = None,
        save_args: dict[str, Any] | None = None,
    ):
        if dataset_type not in ["file", "table"]:
            raise DeltaTableAppenderError(
                f"Invalid dataset type: {dataset_type}. Valid types are 'file' and 'table'"
            )
        self._dataset_type = dataset_type
        self._table = table
        self._schema = schema.rstrip("/")

        if dataset_type == "table":
            if not 1 <= len(schema.split(".")) <= 2:  # noqa PLR2004
                raise DeltaTableAppenderError(
                    f"Invalid table schema: {self._schema}. It must be in the format "
                    "'catalog.schema'"
                )
            self._full_table_path = f"{self._schema}.{self._table}"

            if external_path:
                self._external_path = external_path
                self._is_external_table = True
            else:
                self._is_external_table = False
        else:
            self._full_table_path = f"{self._schema}/{self._table}"
            self._is_external_table = False

        self._save_args = deepcopy(save_args) if save_args else {}

        if "mode" in self._save_args:
            del self._save_args["mode"]

        if "format" in self._save_args:
            del self._save_args["format"]

    @property
    def table(self) -> str:
        return self._table

    @property
    def schema(self) -> str:
        return self._schema

    @property
    def full_table_path(self) -> str:
        return self._full_table_path

    @property
    def is_external_table(self) -> bool:
        return self._is_external_table

    def exists(self) -> bool:
        fullpath = (
            self._full_table_path
            if self._dataset_type == "table"
            else f"DELTA.`{self._full_table_path}`"
        )
        try:
            DeltaTable.forName(get_spark(), fullpath)
        except AnalysisException as exception:
            if "is not a Delta table" in str(exception):
                return False
            raise DeltaTableAppenderError(
                f"Error while checking if delta table exists: {exception!s}"
            ) from exception

        return True

    def append(self, df: DataFrame) -> None:
        if self._dataset_type == "file":
            self._save_as_file(df)
        else:
            self._save_as_table(df)

    def _save_as_file(self, df: DataFrame) -> None:
        df.write.save(
            path=self._full_table_path, format="delta", mode="append", **self._save_args
        )

    def _save_as_table(self, df: DataFrame) -> None:
        _options = {
            "name": self._full_table_path,
            "mode": "append",
            "format": "delta",
            **self._save_args,
        }

        if self._is_external_table:
            _options["path"] = self._external_path

        df.write.saveAsTable(**_options)
