import inspect
import operator
from typing import TYPE_CHECKING

import pandas as pd
import pandas.api.types as pdt

from datasentinel.validation.check.row_level_result.rule import Rule, RuleDataType
from datasentinel.validation.check.row_level_result.utils import evaluate_pass_rate
from datasentinel.validation.check.row_level_result.validation_strategy import (
    ValidationStrategy,
)
from datasentinel.validation.failed_rows_dataset.pandas import PandasFailedRowsDataset
from datasentinel.validation.rule.metric import RuleMetric


if TYPE_CHECKING:
    from collections.abc import Callable


class PandasValidationStrategy(ValidationStrategy):
    def __init__(self) -> None:
        self._compute_instructions: dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {}

    def is_complete(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            df = df[rule.queried_columns]
            return df[df[rule.column[0]].isna()]

        self._compute_instructions[rule.key] = _execute

    def are_complete(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            df = df[[*rule.id_columns, *rule.column]]
            return df[df[list(rule.column)].isnull().any(axis=1)]

        self._compute_instructions[rule.key] = _execute

    def is_unique(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            _df = df[[rule.column[0]]]
            if rule.options.get("ignore_nulls"):
                _df = _df.dropna()
            return _df[_df.duplicated(keep="first")]

        self._compute_instructions[rule.key] = _execute

    def are_unique(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            _df = df[rule.column]
            if rule.options.get("ignore_nulls"):
                _df = _df.dropna(subset=rule.column)
            return _df[_df.duplicated(keep="first")]

        self._compute_instructions[rule.key] = _execute

    def has_pattern(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            df = df[rule.queried_columns]
            return df[~df[rule.column[0]].str.match(rule.value, na=False)]

        self._compute_instructions[rule.key] = _execute

    def is_greater_than(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            df = df[rule.queried_columns]
            return df[df[rule.column[0]] <= rule.value]

        self._compute_instructions[rule.key] = _execute

    def is_greater_or_equal_to(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            df = df[rule.queried_columns]
            return df[df[rule.column[0]] < rule.value]

        self._compute_instructions[rule.key] = _execute

    def is_less_than(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            df = df[rule.queried_columns]
            return df[df[rule.column[0]] >= rule.value]

        self._compute_instructions[rule.key] = _execute

    def is_less_or_equal_to(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            df = df[rule.queried_columns]
            return df[df[rule.column[0]] > rule.value]

        self._compute_instructions[rule.key] = _execute

    def is_equal_to(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            df = df[rule.queried_columns]
            return df[df[rule.column[0]] != rule.value]

        self._compute_instructions[rule.key] = _execute

    def is_between(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            df = df[rule.queried_columns]
            return df[~df[rule.column[0]].between(rule.value[0], rule.value[1])]

        self._compute_instructions[rule.key] = _execute

    def is_in(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            df = df[rule.queried_columns]
            return df[~df[rule.column[0]].isin(rule.value)]

        self._compute_instructions[rule.key] = _execute

    def not_in(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            df = df[rule.queried_columns]
            return df[df[rule.column[0]].isin(rule.value)]

        self._compute_instructions[rule.key] = _execute

    def is_custom(self, rule: Rule) -> None:
        def _execute(df: pd.DataFrame) -> pd.DataFrame:
            if len(inspect.signature(rule.function).parameters) == 1:
                computed_df = rule.function(df)
            else:
                computed_df = rule.function(df, rule.options)
            if "pandas" not in str(type(computed_df)):
                raise ValueError("Custom function does not return a Pandas DataFrame")
            return computed_df

        self._compute_instructions[rule.key] = _execute

    def _generate_compute_instructions(self, rules: dict[str, Rule]) -> None:
        for v in rules.values():
            operator.methodcaller(v.method, v)(self)

    def _compute_bad_records(
        self,
        dataframe: pd.DataFrame,
    ) -> dict[str, pd.DataFrame]:
        """Compute bad records"""
        return {
            k: compute_instruction(dataframe)  # type: ignore
            for k, compute_instruction in self._compute_instructions.items()
        }

    def validate_data_types(self, df: pd.DataFrame, rules: dict[str, Rule]) -> None:
        function_map = {
            RuleDataType.NUMERIC: pdt.is_numeric_dtype,
            RuleDataType.STRING: pdt.is_string_dtype,
            RuleDataType.DATE: pdt.is_datetime64_any_dtype,
            RuleDataType.TIMESTAMP: pdt.is_datetime64_any_dtype,
        }
        for key, rule in rules.items():
            if rule.data_type == RuleDataType.AGNOSTIC:
                continue

            for col in rule.column:
                if not function_map[rule.data_type](df[col]):
                    raise TypeError(
                        f"Column '{col}' type is not compatible with rule '{rule.method}' "
                        f"data type: '{rule.data_type}'"
                    )

    def compute(self, df: pd.DataFrame, rules: dict[str, Rule]) -> list[RuleMetric]:
        rows = df.shape[0]
        self._generate_compute_instructions(rules)
        bad_records = self._compute_bad_records(df)

        rule_metrics = []
        for index, (hash_key, rule) in enumerate(rules.items(), 1):
            bad_records_count = bad_records[hash_key].shape[0]
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
                        PandasFailedRowsDataset(bad_records[rule.key])
                        if bad_records_count > 0
                        else None
                    ),
                )
            )

        return rule_metrics
