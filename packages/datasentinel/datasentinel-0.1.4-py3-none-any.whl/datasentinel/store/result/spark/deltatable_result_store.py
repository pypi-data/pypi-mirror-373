import json
from typing import Any, Literal

from pyspark.sql import DataFrame, Row
from pyspark.sql.types import (
    ArrayType,
    DoubleType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from datasentinel.store.result.core import AbstractResultStore, ResultStoreError
from datasentinel.store.utils.deltatable_appender import DeltaTableAppender
from datasentinel.store.utils.spark_utils import get_spark
from datasentinel.validation.result import DataValidationResult
from datasentinel.validation.rule.metric import RuleMetric


class DeltaTableResultStore(AbstractResultStore):
    def __init__(  # noqa PLR0913
        self,
        name: str,
        table: str,
        schema: str,
        dataset_type: Literal["file", "table"],
        external_path: str | None = None,
        save_args: dict[str, Any] | None = None,
        include_failed_rows: bool = False,
        failed_rows_limit: int = 100,
        disabled: bool = False,
    ):
        super().__init__(name, disabled)
        if include_failed_rows and not failed_rows_limit > 0:
            raise ResultStoreError("Failed rows limit must be greater than 0")
        self._failed_rows_limit = failed_rows_limit
        self._include_failed_records = include_failed_rows
        self._delta_table_appender = DeltaTableAppender(
            table=table,
            schema=schema,
            dataset_type=dataset_type,
            external_path=external_path,
            save_args=save_args,
        )

    def _result_to_df(self, result: DataValidationResult) -> DataFrame:
        rows = []
        for check_result in result.check_results:
            for rule_metric in check_result.rule_metrics:
                rows.append(
                    Row(
                        run_id=str(result.run_id),
                        name=result.name,
                        data_asset=result.data_asset,
                        data_asset_schema=result.data_asset_schema,
                        start_time=result.start_time,
                        end_time=result.end_time,
                        status=result.status.value,
                        check_name=check_result.name,
                        check_level=check_result.level.name,
                        check_class_name=check_result.class_name,
                        check_start_time=check_result.start_time,
                        check_end_time=check_result.end_time,
                        check_status=check_result.status.value,
                        rule_index=rule_metric.id,
                        rule_name=rule_metric.rule,
                        rule_column=rule_metric.column,
                        rule_id_columns=rule_metric.id_columns,
                        rule_value=str(rule_metric.value) if rule_metric.value else None,
                        rule_function=(
                            RuleMetric.function_to_string(rule_metric.function)
                            if rule_metric.function
                            else None
                        ),
                        rule_rows=rule_metric.rows,
                        rule_violations=rule_metric.violations,
                        rule_pass_rate=rule_metric.pass_rate,
                        rule_pass_threshold=rule_metric.pass_threshold,
                        rule_options=(
                            json.dumps(rule_metric.options) if rule_metric.options else None
                        ),
                        rule_failed_rows_dataset=(
                            rule_metric.failed_rows_dataset.to_json(limit=self._failed_rows_limit)
                            if (
                                rule_metric.failed_rows_dataset is not None
                                and self._include_failed_records
                            )
                            else None
                        ),
                        rule_status=rule_metric.status.value,
                    )
                )

        return get_spark().createDataFrame(
            data=rows,
            schema=StructType(
                [
                    StructField(name="run_id", dataType=StringType()),
                    StructField(name="name", dataType=StringType()),
                    StructField(name="data_asset", dataType=StringType()),
                    StructField(name="data_asset_schema", dataType=StringType()),
                    StructField(name="start_time", dataType=TimestampType()),
                    StructField(name="end_time", dataType=TimestampType()),
                    StructField(name="status", dataType=StringType()),
                    StructField(name="check_name", dataType=StringType()),
                    StructField(name="check_level", dataType=StringType()),
                    StructField(name="check_class_name", dataType=StringType()),
                    StructField(name="check_start_time", dataType=TimestampType()),
                    StructField(name="check_end_time", dataType=TimestampType()),
                    StructField(name="check_status", dataType=StringType()),
                    StructField(name="rule_index", dataType=IntegerType()),
                    StructField(name="rule_name", dataType=StringType()),
                    StructField(name="rule_column", dataType=ArrayType(StringType())),
                    StructField(name="rule_id_columns", dataType=ArrayType(StringType())),
                    StructField(name="rule_value", dataType=StringType()),
                    StructField(name="rule_function", dataType=StringType()),
                    StructField(name="rule_rows", dataType=LongType()),
                    StructField(name="rule_violations", dataType=LongType()),
                    StructField(name="rule_pass_rate", dataType=DoubleType()),
                    StructField(name="rule_pass_threshold", dataType=DoubleType()),
                    StructField(name="rule_options", dataType=StringType()),
                    StructField(name="rule_failed_rows_dataset", dataType=StringType()),
                    StructField(name="rule_status", dataType=StringType()),
                ]
            ),
        )

    def store(self, result: DataValidationResult) -> None:
        try:
            self._delta_table_appender.append(self._result_to_df(result))
        except Exception as e:
            raise ResultStoreError(
                f"Error while saving data validation result in delta table: {e!s}"
            ) from e
