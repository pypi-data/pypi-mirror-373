import inspect
import operator
from typing import TYPE_CHECKING

from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from pyspark.sql.types import DateType, NumericType, StringType, TimestampType

from datasentinel.validation.check.row_level_result.rule import Rule, RuleDataType
from datasentinel.validation.check.row_level_result.utils import evaluate_pass_rate
from datasentinel.validation.check.row_level_result.validation_strategy import (
    ValidationStrategy,
)
from datasentinel.validation.failed_rows_dataset.spark import SparkFailedRowsDataset
from datasentinel.validation.rule.metric import RuleMetric


if TYPE_CHECKING:
    from collections.abc import Callable


class PysparkValidationStrategy(ValidationStrategy):
    def __init__(self) -> None:
        """Determine the computational options for Rules"""
        self._compute_instructions: dict[str, Callable[[DataFrame], DataFrame]] = {}

    def is_complete(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            return df.select(*rule.queried_columns).where(F.col(rule.column[0]).isNull())

        self._compute_instructions[rule.key] = _execute

    def are_complete(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            return df.select(*rule.queried_columns).where(
                " OR ".join([f"{column} IS NULL" for column in rule.column])
            )

        self._compute_instructions[rule.key] = _execute

    def is_unique(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            _df = df.select(rule.column[0])
            if rule.options.get("ignore_nulls"):
                _df = _df.where(F.col(rule.column[0]).isNotNull())
            return (
                _df.groupBy(rule.column[0])
                .count()
                .where(F.col("count") > 1)
                .select(rule.column[0])
            )

        self._compute_instructions[rule.key] = _execute

    def are_unique(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            _df = df.select(*rule.column)
            if rule.options.get("ignore_nulls"):
                _df = _df.where(" AND ".join([f"{column} IS NOT NULL" for column in rule.column]))
            return _df.groupBy(rule.column).count().where(F.col("count") > 1).select(*rule.column)

        self._compute_instructions[rule.key] = _execute

    def has_pattern(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            return df.select(*rule.queried_columns).filter(
                ~F.col(rule.column[0]).rlike(rule.value)
            )

        self._compute_instructions[rule.key] = _execute

    def is_greater_than(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            return df.select(*rule.queried_columns).where(F.col(rule.column[0]) <= rule.value)

        self._compute_instructions[rule.key] = _execute

    def is_greater_or_equal_to(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            return df.select(
                *rule.queried_columns,
            ).where(F.col(rule.column[0]) < rule.value)

        self._compute_instructions[rule.key] = _execute

    def is_less_than(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            return df.select(*rule.queried_columns).where(F.col(rule.column[0]) >= rule.value)

        self._compute_instructions[rule.key] = _execute

    def is_less_or_equal_to(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            return df.select(
                *rule.queried_columns,
            ).where(F.col(rule.column[0]) > rule.value)

        self._compute_instructions[rule.key] = _execute

    def is_equal_to(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            return df.select(
                *rule.queried_columns,
            ).where(F.col(rule.column[0]) != rule.value)

        self._compute_instructions[rule.key] = _execute

    def is_between(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            return df.select(
                *rule.queried_columns,
            ).where(~F.col(rule.column[0]).between(rule.value[0], rule.value[1]))

        self._compute_instructions[rule.key] = _execute

    def is_in(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            return df.select(
                *rule.queried_columns,
            ).filter(~F.col(rule.column[0]).isin(rule.value))

        self._compute_instructions[rule.key] = _execute

    def not_in(self, rule: Rule) -> None:
        def _execute(df: DataFrame) -> DataFrame:
            return df.select(
                *rule.queried_columns,
            ).filter(F.col(rule.column[0]).isin(rule.value))

        self._compute_instructions[rule.key] = _execute

    def is_custom(self, rule: Rule) -> None:
        def _execute(df: DataFrame):
            if len(inspect.signature(rule.function).parameters) == 1:
                computed_df = rule.function(df)
            else:
                computed_df = rule.function(df, rule.options)
            if "pyspark" not in str(type(computed_df)):
                raise ValueError("Custom function does not return a PySpark DataFrame")
            return computed_df

        self._compute_instructions[rule.key] = _execute

    def _generate_compute_instructions(self, rules: dict[str, Rule]) -> None:
        for k, v in rules.items():
            operator.methodcaller(v.method, v)(self)

    def _compute_bad_records(
        self,
        dataframe: DataFrame,
    ) -> dict[str, DataFrame]:
        """Compute rules through spark transform"""
        return {
            k: compute_instruction(dataframe)  # type: ignore
            for k, compute_instruction in self._compute_instructions.items()
        }

    def validate_data_types(self, df: DataFrame, rules: dict[str, Rule]) -> None:
        """Validate the datatype of each column according to the CheckDataType of the
        rule's method"""
        types_map = {
            RuleDataType.NUMERIC: NumericType,
            RuleDataType.STRING: StringType,
            RuleDataType.DATE: DateType,
            RuleDataType.TIMESTAMP: TimestampType,
        }
        for key, rule in rules.items():
            if rule.data_type == RuleDataType.AGNOSTIC:
                continue
            for col in rule.column:
                if not isinstance(df.schema[col].dataType, types_map[rule.data_type]):
                    raise TypeError(
                        f"Column '{col}' type is not compatible with rule '{rule.method}' "
                        f"data type: '{rule.data_type}'"
                    )

    def compute(self, df: DataFrame, rules: dict[str, Rule]) -> list[RuleMetric]:
        """Compute and returns calculated rule metrics"""
        rows = df.count()
        self._generate_compute_instructions(rules)
        bad_records = self._compute_bad_records(df)

        rule_metrics = []
        for index, (hash_key, rule) in enumerate(rules.items(), 1):
            bad_records_count = bad_records[hash_key].count()
            pass_rate = evaluate_pass_rate(rows, bad_records_count)
            rule_metrics.append(
                RuleMetric(
                    id=index,
                    rule=rule.method,
                    column=rule.column,
                    id_columns=rule.id_columns,
                    value=rule.value,
                    function=rule.function,
                    rows=rows,
                    violations=bad_records_count,
                    pass_rate=pass_rate,
                    pass_threshold=rule.pass_threshold,
                    options=rule.options,
                    failed_rows_dataset=(
                        SparkFailedRowsDataset(bad_records[rule.key])
                        if bad_records_count > 0
                        else None
                    ),
                )
            )

        return rule_metrics
