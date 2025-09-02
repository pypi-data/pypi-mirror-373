from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from datasentinel.validation.core import NotifyOnEvent
from datasentinel.validation.data_validation import DataValidation


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class ValidationWorkflow:
    data_validation: DataValidation
    result_stores: list[str] = Field(default_factory=list)
    notifiers_by_event: dict[NotifyOnEvent, list[str]] = Field(default_factory=dict)
