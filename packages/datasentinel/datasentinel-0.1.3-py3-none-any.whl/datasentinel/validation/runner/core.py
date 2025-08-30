from abc import ABC, abstractmethod

from datasentinel.core import DataSentinelError
from datasentinel.notification.notifier.core import AbstractNotifierManager
from datasentinel.store.result.core import AbstractResultStoreManager
from datasentinel.validation.workflow import ValidationWorkflow


class RunnerError(DataSentinelError):
    """Base class for runner errors."""


class NoDatasetDefinedError(RunnerError):
    pass


class CriticalCheckFailedError(RunnerError):
    pass


class AbstractWorkflowRunner(ABC):
    """Base class for all validation workflow runner implementations."""

    @abstractmethod
    def run(
        self,
        validation_workflow: ValidationWorkflow,
        notifier_manager: AbstractNotifierManager,
        result_store_manager: AbstractResultStoreManager,
    ) -> None:
        """Run a validation workflow."""
