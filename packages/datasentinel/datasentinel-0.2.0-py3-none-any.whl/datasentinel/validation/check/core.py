from abc import ABC, abstractmethod
import enum
from typing import Any

from datasentinel.core import DataSentinelError
from datasentinel.validation.check.level import CheckLevel
from datasentinel.validation.check.result import CheckResult
from datasentinel.validation.check.utils import get_type


class CheckError(DataSentinelError):
    pass


class BadArgumentError(CheckError):
    pass


class UnsupportedDataframeTypeError(CheckError):
    pass


class EmptyCheckError(CheckError):
    pass


class DataframeType(enum.Enum):
    PYSPARK = "pyspark"
    PANDAS = "pandas"

    @classmethod
    def from_df(cls, df: Any) -> "DataframeType":
        _type = get_type(df)

        if "pyspark" in _type:
            return DataframeType.PYSPARK
        elif "pandas" in _type:
            return DataframeType.PANDAS
        else:
            raise ValueError(f"{type(df)} is not a valid dataframe type.")


class AbstractCheck(ABC):
    """Base class for all data quality check implementations."""

    def __init__(
        self,
        level: CheckLevel,
        name: str,
    ):
        self._level = level
        self._name = name

    @property
    def name(self) -> str:
        """Return the name of the check."""
        return self._name

    @property
    def level(self) -> CheckLevel:
        """Return the level of the check."""
        return self._level

    @abstractmethod
    def validate(self, df: Any) -> CheckResult:
        """Validate the given dataframe.

        Args:
            df: The dataframe to validate.

        Returns:
            The result of data quality check applied to the dataframe.
        """
