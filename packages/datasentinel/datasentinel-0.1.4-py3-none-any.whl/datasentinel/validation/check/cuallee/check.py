from collections.abc import Callable
from datetime import datetime
from typing import Any

from cuallee import (
    Check,
    CheckLevel as CualleeCheckLevel,
)
from typing_extensions import Self

from datasentinel.validation.check.core import (
    AbstractCheck,
    DataframeType,
)
from datasentinel.validation.check.level import CheckLevel
from datasentinel.validation.check.result import CheckResult
from datasentinel.validation.check.utils import to_df_if_delta_table
from datasentinel.validation.rule.metric import RuleMetric


def _cuallee_check_level(level: CheckLevel) -> CualleeCheckLevel:
    # Correct:
    return CualleeCheckLevel.WARNING if level == CheckLevel.WARNING else CualleeCheckLevel.ERROR


class CualleeCheck(AbstractCheck):
    """Cuallee check implementation."""

    def __init__(self, level: CheckLevel, name: str):
        """Initialize a new CualleeCheck instance.

        Args:
            level: The severity level of the check.
            name: The name of the check.
        """
        self._check = Check(level=_cuallee_check_level(level=level), name=name)
        super().__init__(level, name)

    def is_complete(self, column: str, pct: float = 1.0) -> Self:
        """Check if values in the specified column are complete (non-null).

        Args:
            column: The name of the column to check.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_complete(column=column, pct=pct)
        return self

    def is_empty(self, column: str, pct: float = 1.0) -> Self:
        """Check if values in the specified column are empty.

        Args:
            column: The name of the column to check.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_empty(column=column, pct=pct)
        return self

    def are_complete(self, column: list[str], pct: float = 1.0) -> Self:
        """Check if values in the specified columns are complete (non-null).

        Args:
            column: List of column names to check.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.are_complete(column=column, pct=pct)
        return self

    def is_unique(
        self,
        column: str,
        pct: float = 1.0,
        approximate: bool = False,
        ignore_nulls: bool = False,
    ) -> Self:
        """Check if values in the specified column are unique.

        Args:
            column: The name of the column to check.
            pct: The minimum passing ratio required (0.0 to 1.0).
            approximate: If True, uses an approximate algorithm for better performance.
            ignore_nulls: If True, null values are not counted when checking uniqueness.
        """
        self._check.is_unique(
            column=column, pct=pct, approximate=approximate, ignore_nulls=ignore_nulls
        )
        return self

    def is_primary_key(self, column: str, pct: float = 1.0) -> Self:
        """Check if the column can be used as a primary key.

        Args:
            column: The name of the column to check.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_primary_key(column=column, pct=pct)
        return self

    def are_unique(
        self,
        column: list[str],
        pct: float = 1.0,
    ) -> Self:
        """Check if the combination of columns is unique.

        Args:
            column: List of column names to check for uniqueness.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.are_unique(column=column, pct=pct)
        return self

    def is_composite_key(self, column: list[str], pct: float = 1.0) -> Self:
        """Check if the combination of columns can be used as a composite key.

        Args:
            column: List of column names to check.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_composite_key(column=column, pct=pct)
        return self

    def is_greater_than(self, column: str, value: float, pct: float = 1.0) -> Self:
        """Check if values in the column are greater than the specified value.

        Args:
            column: The name of the column to check.
            value: The value to compare against.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_greater_than(column=column, value=value, pct=pct)
        return self

    def is_positive(self, column: str, pct: float = 1.0) -> Self:
        """Check if values in the column are positive.

        Args:
            column: The name of the column to check.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_positive(column=column, pct=pct)
        return self

    def is_greater_or_equal_to(self, column: str, value: float, pct: float = 1.0) -> Self:
        """Check if values in the column are greater than or equal to the specified value.

        Args:
            column: The name of the column to check.
            value: The value to compare against.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_greater_or_equal_than(column=column, value=value, pct=pct)
        return self

    def is_in_millions(self, column: str, pct: float = 1.0) -> Self:
        """Check if values in the column are in millions.

        Args:
            column: The name of the column to check.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_in_millions(column=column, pct=pct)
        return self

    def is_in_billions(self, column: str, pct: float = 1.0) -> Self:
        """Check if values in the column are in billions.

        Args:
            column: The name of the column to check.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_in_billions(column=column, pct=pct)
        return self

    def is_less_than(self, column: str, value: float, pct: float = 1.0) -> Self:
        """Check if values in the column are less than the specified value.

        Args:
            column: The name of the column to check.
            value: The value to compare against.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_less_than(column=column, value=value, pct=pct)
        return self

    def is_negative(self, column: str, pct: float = 1.0) -> Self:
        """Check if values in the column are negative.

        Args:
            column: The name of the column to check.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_negative(column=column, pct=pct)
        return self

    def is_less_or_equal_to(self, column: str, value: float, pct: float = 1.0) -> Self:
        """Check if values in the column are less than or equal to the specified value.

        Args:
            column: The name of the column to check.
            value: The value to compare against.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_less_or_equal_than(column=column, value=value, pct=pct)
        return self

    def is_equal_to(self, column: str, value: float, pct: float = 1.0) -> Self:
        """Check if values in the column are equal to the specified value.

        Args:
            column: The name of the column to check.
            value: The value to compare against.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_equal_than(column=column, value=value, pct=pct)
        return self

    def has_pattern(self, column: str, value: str, pct: float = 1.0) -> Self:
        """Check if values in the column match the specified pattern.

        Args:
            column: The name of the column to check.
            value: The regex pattern to match against.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.has_pattern(column=column, value=value, pct=pct)
        return self

    def is_legit(self, column: str, pct: float = 1.0) -> Self:
        """Check if values in the column are legitimate (non-null and non-blank).

        Args:
            column: The name of the column to check.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_legit(column=column, pct=pct)
        return self

    def has_min(self, column: str, value: float) -> Self:
        """Check if the minimum value in the column equals the specified value.

        Args:
            column: The name of the column to check.
            value: The expected minimum value.
        """
        self._check.has_min(column=column, value=value)
        return self

    def has_max(self, column: str, value: float) -> Self:
        """Check if the maximum value in the column equals the specified value.

        Args:
            column: The name of the column to check.
            value: The expected maximum value.
        """
        self._check.has_max(column=column, value=value)
        return self

    def has_std(self, column: str, value: float) -> Self:
        """Check if the standard deviation of the column equals the specified value.

        Args:
            column: The name of the column to check.
            value: The expected standard deviation.
        """
        self._check.has_std(column=column, value=value)
        return self

    def has_mean(self, column: str, value: float) -> Self:
        """Check if the mean of the column equals the specified value.

        Args:
            column: The name of the column to check.
            value: The expected mean value.
        """
        self._check.has_mean(column=column, value=value)
        return self

    def has_sum(self, column: str, value: float) -> Self:
        """Check if the sum of the column equals the specified value.

        Args:
            column: The name of the column to check.
            value: The expected sum.
        """
        self._check.has_sum(column=column, value=value)
        return self

    def is_between(self, column: str, value: list, pct: float = 1.0) -> Self:
        """Check if values in the column are between the specified range.

        Args:
            column: The name of the column to check.
            value: A list of two values representing the range [min, max].
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.is_between(column=column, value=tuple(value), pct=pct)
        return self

    def not_contained_in(self, column: str, value: list, pct: float = 1.0) -> Self:
        """Check if values in the column are not contained in the specified list.

        Args:
            column: The name of the column to check.
            value: List of values that should not be present.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.not_contained_in(column=column, value=value, pct=pct)
        return self

    def not_in(self, column: str, value: list, pct: float = 1.0) -> Self:
        """Check if values in the column are not in the specified list.

        Args:
            column: The name of the column to check.
            value: List of values that should not be present.
            pct: The minimum passing ratio required (0.0 to 1.0).
        """
        self._check.not_in(column=column, value=tuple(value), pct=pct)
        return self

    def is_contained_in(self, column: str, value: tuple | list, pct: float = 1.0) -> Self:
        self._check.is_contained_in(column=column, value=value, pct=pct)
        return self

    def is_in(self, column: str, value: list, pct: float = 1.0) -> Self:
        self._check.is_in(column=column, value=tuple(value), pct=pct)
        return self

    def is_t_minus_n(
        self,
        column: str,
        value: int,
        pct: float = 1.0,
        options: dict[str, str] | None = None,
    ) -> Self:
        options = options or {}
        self._check.is_t_minus_n(column=column, value=value, pct=pct, options=options)
        return self

    def is_t_minus_1(
        self,
        column: str,
        pct: float = 1.0,
    ) -> Self:
        self._check.is_t_minus_1(column=column, pct=pct)
        return self

    def is_t_minus_2(
        self,
        column: str,
        pct: float = 1.0,
    ) -> Self:
        self._check.is_t_minus_2(column=column, pct=pct)
        return self

    def is_t_minus_3(
        self,
        column: str,
        pct: float = 1.0,
    ) -> Self:
        self._check.is_t_minus_3(column=column, pct=pct)
        return self

    def is_yesterday(
        self,
        column: str,
        pct: float = 1.0,
    ) -> Self:
        self._check.is_yesterday(column=column, pct=pct)
        return self

    def is_today(
        self,
        column: str,
        pct: float = 1.0,
    ) -> Self:
        self._check.is_today(column=column, pct=pct)
        return self

    def has_percentile(
        self,
        column: str,
        value: float,
        percentile: float,
        precision: int = 10000,
    ) -> Self:
        self._check.has_percentile(
            column=column, value=value, percentile=percentile, precision=precision
        )
        return self

    def is_inside_interquartile_range(
        self, column: str, value: list[float] | None = None, pct: float = 1.0
    ) -> Self:
        self._check.is_inside_interquartile_range(column=column, value=value, pct=pct)
        return self

    def has_max_by(self, column_source: str, column_target: str, value: float | str) -> Self:
        self._check.has_max_by(
            column_source=column_source, column_target=column_target, value=value
        )
        return self

    def has_min_by(self, column_source: str, column_target: str, value: float | str) -> Self:
        self._check.has_min_by(
            column_source=column_source, column_target=column_target, value=value
        )
        return self

    def has_correlation(
        self,
        column_left: str,
        column_right: str,
        value: float,
    ) -> Self:
        self._check.has_correlation(
            column_left=column_left, column_right=column_right, value=value
        )
        return self

    def satisfies(
        self,
        column: str,
        predicate: str,
        pct: float = 1.0,
        options: dict[str, str] | None = None,
    ) -> Self:
        options = options or {}
        self._check.satisfies(column=column, predicate=predicate, pct=pct, options=options)
        return self

    def has_cardinality(
        self,
        column: str,
        value: int,
    ) -> Self:
        self._check.has_cardinality(column=column, value=value)
        return self

    def has_infogain(
        self,
        column: str,
        pct: float = 1.0,
    ) -> Self:
        self._check.has_infogain(column=column, pct=pct)
        return self

    def has_entropy(
        self,
        column: str,
        value: float,
        tolerance: float = 0.01,
    ) -> Self:
        self._check.has_entropy(column=column, value=value, tolerance=tolerance)
        return self

    def is_on_weekday(self, column: str, pct: float = 1.0) -> Self:
        self._check.is_on_weekday(column=column, pct=pct)
        return self

    def is_on_weekend(self, column: str, pct: float = 1.0) -> Self:
        self._check.is_on_weekend(column=column, pct=pct)
        return self

    def is_on_monday(self, column: str, pct: float = 1.0) -> Self:
        self._check.is_on_monday(column=column, pct=pct)
        return self

    def is_on_tuesday(self, column: str, pct: float = 1.0) -> Self:
        self._check.is_on_tuesday(column=column, pct=pct)
        return self

    def is_on_wednesday(self, column: str, pct: float = 1.0) -> Self:
        self._check.is_on_wednesday(column=column, pct=pct)
        return self

    def is_on_thursday(self, column: str, pct: float = 1.0) -> Self:
        self._check.is_on_thursday(column=column, pct=pct)
        return self

    def is_on_friday(self, column: str, pct: float = 1.0) -> Self:
        self._check.is_on_friday(column=column, pct=pct)
        return self

    def is_on_saturday(self, column: str, pct: float = 1.0) -> Self:
        self._check.is_on_saturday(column=column, pct=pct)
        return self

    def is_on_sunday(self, column: str, pct: float = 1.0) -> Self:
        self._check.is_on_sunday(column=column, pct=pct)
        return self

    def is_on_schedule(self, column: str, value: list, pct: float = 1.0) -> Self:
        self._check.is_on_schedule(column=column, value=tuple(value), pct=pct)
        return self

    def is_daily(
        self,
        column: str,
        value: list[int] | None = None,
        pct: float = 1.0,
    ) -> Self:
        self._check.is_daily(column=column, value=value, pct=pct)
        return self

    def has_workflow(
        self,
        column_group: str,
        column_event: str,
        column_order: str,
        edges: list[tuple[str]],
        pct: float = 1.0,
    ) -> Self:
        self._check.has_workflow(
            column_group=column_group,
            column_event=column_event,
            column_order=column_order,
            edges=edges,
            pct=pct,
        )
        return self

    def is_custom(
        self,
        column: str | list[str],
        fn: Callable,
        pct: float = 1.0,
        options: dict[str, str] | None = None,
    ) -> Self:
        options = options or {}
        self._check.is_custom(column=column, fn=fn, pct=pct, options=options)
        return self

    @staticmethod
    def _format_rule_column(column: str | list[str] | tuple[str] | None) -> list[str]:
        if column is None:
            return []
        if isinstance(column, str):
            return [column]

        if isinstance(column, tuple):
            return list(column)

        return column

    def _get_rule_metrics_pyspark(
        self,
        cuallee_result: Any,
    ) -> list[RuleMetric]:
        return [
            RuleMetric(
                id=row.id,
                rule=row.rule,
                column=self._format_rule_column(self._check.rules[i].column),
                value=(
                    self._check.rules[i].value
                    if not row.rule == "is_custom" and not self._check.rules[i].value == "N/A"
                    else None
                ),
                function=(self._check.rules[i].value if row.rule == "is_custom" else None),
                rows=row.rows,
                violations=row.violations,
                pass_rate=row.pass_rate,
                pass_threshold=row.pass_threshold,
                options=self._check.rules[i].options,
                failed_rows_dataset=None,
            )
            for i, row in enumerate(cuallee_result.collect())
        ]

    def _get_rule_metrics_pandas(
        self,
        cuallee_result: Any,
    ) -> list[RuleMetric]:
        return [
            RuleMetric(
                id=row["id"],
                rule=row["rule"],
                column=self._format_rule_column(self._check.rules[i].column),
                value=(
                    self._check.rules[i].value
                    if not row["rule"] == "is_custom" and not self._check.rules[i].value == "N/A"
                    else None
                ),
                function=(self._check.rules[i].value if row["rule"] == "is_custom" else None),
                rows=row["rows"],
                violations=row["violations"],
                pass_rate=row["pass_rate"],
                pass_threshold=row["pass_threshold"],
                options=self._check.rules[i].options,
                failed_rows_dataset=None,
            )
            for i, (index, row) in enumerate(cuallee_result.iterrows())
        ]

    def _to_check_result(
        self, cuallee_result: Any, start_time: datetime, end_time: datetime
    ) -> CheckResult:
        df_type = DataframeType.from_df(cuallee_result)

        if df_type == DataframeType.PYSPARK:
            rule_metrics = self._get_rule_metrics_pyspark(cuallee_result=cuallee_result)
        elif df_type == DataframeType.PANDAS:
            rule_metrics = self._get_rule_metrics_pandas(cuallee_result=cuallee_result)

        return CheckResult(
            name=self.name,
            level=self.level,
            class_name=self.__class__.__name__,
            start_time=start_time,
            end_time=end_time,
            rule_metrics=rule_metrics,
        )

    def validate(self, df: Any) -> CheckResult:
        df = to_df_if_delta_table(df=df)

        start_time = datetime.now()
        result = self._check.validate(df)
        end_time = datetime.now()

        return self._to_check_result(
            cuallee_result=result, start_time=start_time, end_time=end_time
        )
