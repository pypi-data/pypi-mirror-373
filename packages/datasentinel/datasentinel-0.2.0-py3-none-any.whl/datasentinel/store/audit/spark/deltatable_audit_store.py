from datetime import date, datetime
import json
from typing import Any, Literal

from pyspark.sql import DataFrame, Row
from pyspark.sql.types import (
    ArrayType,
    BooleanType,
    DataType,
    DateType,
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from datasentinel.store.audit.core import AbstractAuditStore, AuditStoreError
from datasentinel.store.audit.row import BaseAuditRow, FieldInfo
from datasentinel.store.utils.deltatable_appender import DeltaTableAppender
from datasentinel.store.utils.spark_utils import get_spark


class DeltaTableAuditStore(AbstractAuditStore):
    def __init__(
        self,
        name: str,
        table: str,
        schema: str,
        dataset_type: Literal["file", "table"],
        external_path: str | None = None,
        save_args: dict[str, Any] | None = None,
        disabled: bool = False,
    ):
        super().__init__(name, disabled)
        self._delta_table_appender = DeltaTableAppender(
            table=table,
            schema=schema,
            dataset_type=dataset_type,
            external_path=external_path,
            save_args=save_args,
        )

    def append(self, row: BaseAuditRow) -> None:
        try:
            self._delta_table_appender.append(self._audit_row_to_df(row))
        except Exception as e:
            raise AuditStoreError(f"Failed to append row to audit store. Error: {e!s}") from e

    def _audit_row_to_df(self, row: BaseAuditRow) -> DataFrame:
        row_fields = row.row_fields
        return get_spark().createDataFrame(
            data=[
                Row(
                    **{
                        field_name: self._format_field_value(
                            field_info=row_fields.get(field_name), value=value
                        )
                        for field_name, value in row.to_dict().items()
                    }
                )
            ],
            schema=StructType(
                [
                    StructField(
                        name=field_name,
                        dataType=self._infer_spark_type(field_info=field_info),
                    )
                    for field_name, field_info in row_fields.items()
                ]
            ),
        )

    @staticmethod
    def _format_field_value(field_info: FieldInfo, value: Any) -> Any:
        if value is None or field_info.type in {int, str, float, bool, datetime, date, list}:
            return value
        elif field_info.type in {tuple, set}:
            return list(value)
        else:
            return json.dumps(value)

    def _infer_spark_type(self, field_info: FieldInfo) -> DataType | type[DataType]:
        type_map = {
            int: LongType(),
            str: StringType(),
            bool: BooleanType(),
            float: DoubleType(),
            datetime: TimestampType(),
            date: DateType(),
        }
        if field_info.type in {list, tuple, set}:
            if field_info.args is None or len(field_info.args) != 1:  # pragma: no cover
                raise AuditStoreError("Unsupported collection type")
            return ArrayType(type_map[field_info.args[0]])

        return type_map.get(field_info.type, StringType())
