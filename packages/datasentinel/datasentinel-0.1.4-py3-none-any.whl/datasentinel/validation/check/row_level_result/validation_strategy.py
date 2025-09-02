from abc import ABC, abstractmethod
from typing import Any

from datasentinel.validation.check.row_level_result.rule import Rule
from datasentinel.validation.rule.metric import RuleMetric


class ValidationStrategy(ABC):
    """An interface for validation strategies to adhere to"""

    @abstractmethod
    def validate_data_types(self, df: Any, rules: dict[str, Rule]) -> None:
        """Validate that each rule evaluated columns have correct data types

        Args:
            df: The dataframe to validate
            rules: The rules to validate

        Raises:
            CheckError if validation fails
        """

    @abstractmethod
    def compute(self, df: Any, rules: dict[str, Rule]) -> list[RuleMetric]:
        """Compute and return calculated rule metrics

        Args:
            df: Dataframe to validate
            rules: Rules to compute metrics for

        Returns:
            A list with metrics computed for each rule evaluated
        """
