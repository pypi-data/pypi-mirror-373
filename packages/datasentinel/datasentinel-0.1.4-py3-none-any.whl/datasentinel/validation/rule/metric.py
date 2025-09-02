from collections.abc import Callable
from datetime import date, datetime
from typing import Any

from pydantic import ConfigDict, model_validator
from pydantic.dataclasses import dataclass
from typing_extensions import Self

from datasentinel.validation.failed_rows_dataset.core import AbstractFailedRowsDataset
from datasentinel.validation.status import Status


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class RuleMetric:
    """Represent the result metrics of the evaluation of a data quality rule.

    Attributes:
        id: The id of the rule metric.
        rule: The name of the rule that was evaluated.
        column: The column or columns that the rule evaluated.
        id_columns: The ID columns used to identify failed rows if they were specified.
        value: The value of the rule.
        function: The function used to evaluate the rule if one was supplied.
        rows: The number of rows analyzed.
        violations: The number of rows that didn't pass the rule.
        pass_rate: The pass rate representing the percentage of rows that passed the rule.
        pass_threshold: The pass threshold set for the rule.
        options: The options set for the rule if any.
        failed_rows_dataset: The failed rows dataset containing the rows that failed the rule
            if there were any violations and if they were computed.
    """

    id: int
    rule: str
    rows: int
    violations: int
    pass_rate: float
    pass_threshold: float
    value: (
        int
        | float
        | str
        | datetime
        | date
        | list[int]
        | list[float]
        | list[str]
        | list[datetime]
        | list[date]
        | None
    ) = None
    function: Callable | None = None
    options: dict[str, Any] | None = None
    column: list[str] | None = None
    id_columns: list[str] | None = None
    failed_rows_dataset: AbstractFailedRowsDataset | None = None

    @model_validator(mode="after")
    def validate_violations_less_than_rows(self) -> Self:
        if self.violations > self.rows:
            raise ValueError("Violations cannot be greater than rows")

        return self

    @model_validator(mode="after")
    def validate_pass_rate_higher_than_1(self) -> Self:
        if self.pass_rate > 1.0:
            raise ValueError("Pass rate cannot be greater than 1.0 (100%)")

        return self

    @property
    def status(self):
        """Return the status of the rule."""
        return Status.PASS if self.pass_rate >= self.pass_threshold else Status.FAIL

    @staticmethod
    def function_to_string(function: Callable) -> str:
        return f"{function.__module__}.{function.__name__}"

    def to_dict(self) -> dict[str, Any]:
        """Return the rule metric as a dictionary."""
        return {
            "id": self.id,
            "rule": self.rule,
            "column": self.column,
            "id_columns": self.id_columns,
            "value": self.value,
            "function": self.function,
            "rows": self.rows,
            "violations": self.violations,
            "pass_rate": self.pass_rate,
            "pass_threshold": self.pass_threshold,
            "options": self.options,
            "failed_rows_dataset": self.failed_rows_dataset,
            "status": self.status,
        }
