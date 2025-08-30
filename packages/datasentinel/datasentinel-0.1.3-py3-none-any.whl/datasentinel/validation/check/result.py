from datetime import datetime
from typing import Any

from pydantic.dataclasses import dataclass

from datasentinel.validation.check.level import CheckLevel
from datasentinel.validation.rule.metric import RuleMetric
from datasentinel.validation.status import Status


@dataclass(frozen=True)
class CheckResult:
    """Represent the result of a data quality check.

    Attributes:
        name: The name of the check.
        level: The severity level of the check.
        class_name: The name of the python class of the check that was applied.
        start_time: The start time of the check.
        end_time: The end time of the check.
        rule_metrics: A list with the metrics computed for each rule applied
            in the check.
    """

    name: str
    level: CheckLevel
    class_name: str
    start_time: datetime
    end_time: datetime
    rule_metrics: list[RuleMetric]

    @property
    def status(self) -> Status:
        """Return the status of the check."""
        return (
            Status.PASS
            if all([metric.status == Status.PASS for metric in self.rule_metrics])
            else Status.FAIL
        )

    @property
    def failed_rules(self) -> list[RuleMetric]:
        """Return the metrics of the rules that failed."""
        return [metric for metric in self.rule_metrics if metric.status == Status.FAIL]

    @property
    def failed_rules_count(self) -> int:
        """Return the number of rules that failed."""
        return len(self.failed_rules)

    def to_dict(self) -> dict[str, Any]:
        """Return the result of the check as a dictionary."""
        return {
            "name": self.name,
            "level": self.level.name,
            "check_class": self.class_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "rule_metrics": [rule_metric.to_dict() for rule_metric in self.rule_metrics],
            "status": self.status,
        }
