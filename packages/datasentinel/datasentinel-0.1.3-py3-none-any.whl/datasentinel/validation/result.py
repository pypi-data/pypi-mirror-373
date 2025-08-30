from datetime import datetime
from typing import Any

from pydantic import ConfigDict, model_validator
from pydantic.dataclasses import dataclass
from typing_extensions import Self
from ulid import ULID

from datasentinel.validation.check.level import CheckLevel
from datasentinel.validation.check.result import CheckResult
from datasentinel.validation.status import Status


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class DataValidationResult:
    """Represent the result of a data validation process.

    Attributes:
        run_id: The unique identifier of the validation process.
        name: The name of the validation process.
        data_asset: The name of the data asset validated.
        data_asset_schema: The schema of the data asset validated.
        start_time: The start time of the validation process.
        end_time: The end time of the validation process.
        check_results: A list with the results of the data quality checks applied.
    """

    run_id: ULID
    name: str
    data_asset: str
    start_time: datetime
    end_time: datetime
    check_results: list[CheckResult]
    data_asset_schema: str | None = None

    @model_validator(mode="after")
    def validate_start_end_time(self) -> Self:
        if self.start_time > self.end_time:
            raise ValueError("Start time must be before end time")
        return self

    @property
    def status(self) -> Status:
        return (
            Status.PASS
            if all([check_result.status == Status.PASS for check_result in self.check_results])
            else Status.FAIL
        )

    @property
    def checks_count(self) -> int:
        return len(self.check_results)

    @property
    def failed_checks(self) -> list[CheckResult]:
        return [
            check_result
            for check_result in self.check_results
            if check_result.status == Status.FAIL
        ]

    @property
    def failed_checks_count(self) -> int:
        return len(self.failed_checks)

    def failed_checks_by_level(self, level: CheckLevel) -> list[CheckResult]:
        return [
            check_result for check_result in self.failed_checks if check_result.level == level
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "name": self.name,
            "data_asset": self.data_asset,
            "data_asset_schema": self.data_asset_schema,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "check_results": [check_result.to_dict() for check_result in self.check_results],
            "status": self.status,
        }
