from datetime import datetime

from pydantic import ConfigDict, field_validator
from pydantic.dataclasses import dataclass
from ulid import ULID

from datasentinel.validation.check.core import AbstractCheck
from datasentinel.validation.data_asset.core import AbstractDataAsset
from datasentinel.validation.result import DataValidationResult


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class DataValidation:
    """Represent the parametrization of a data validation process.

    Attributes:
        name: The name of the data validation process.
        check_list: A list with the data quality checks to be applied to
            the data asset.
        data_asset: The data asset to be validated.
    """

    name: str
    check_list: list[AbstractCheck]
    data_asset: AbstractDataAsset

    @field_validator("check_list", mode="after")
    def validate_check_list(cls, check_list: list[AbstractCheck]) -> list[AbstractCheck]:
        if not check_list:
            raise ValueError("Data validation must have at least one check")

        if len(set(check.name for check in check_list)) != len(check_list):
            raise ValueError("Data validation checks must have unique names")
        return check_list

    @property
    def checks_count(self) -> int:
        return len(self.check_list)

    def check_exists(self, check_name: str) -> bool:
        return any(check.name == check_name for check in self.check_list)

    def run(self) -> DataValidationResult:
        data = self.data_asset.load()
        start_time = datetime.now()
        check_results = [check.validate(data) for check in self.check_list]
        end_time = datetime.now()

        return DataValidationResult(
            run_id=ULID(),
            name=self.name,
            data_asset=self.data_asset.name,
            data_asset_schema=self.data_asset.schema,
            start_time=start_time,
            end_time=end_time,
            check_results=check_results,
        )
