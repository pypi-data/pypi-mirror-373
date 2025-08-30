import logging
import threading
from typing import ClassVar

from ulid import ULID

from datasentinel.notification.notifier.core import AbstractNotifierManager
from datasentinel.notification.notifier.manager import NotifierManager
from datasentinel.session.core import (
    SessionAlreadyExistsError,
    SessionNotSpecifiedError,
)
from datasentinel.store.audit.core import AbstractAuditStoreManager
from datasentinel.store.audit.manager import AuditStoreManager
from datasentinel.store.result.core import AbstractResultStoreManager
from datasentinel.store.result.manager import ResultStoreManager
from datasentinel.validation.runner.core import AbstractWorkflowRunner
from datasentinel.validation.runner.simple_workflow_runner import SimpleWorkflowRunner
from datasentinel.validation.workflow import ValidationWorkflow


class DataSentinelSession:
    """Entry point to access all the functionalities of DataSentinel."""

    _active_sessions: ClassVar[dict[str, "DataSentinelSession"]] = {}
    _lock = threading.Lock()

    def __init__(
        self,
        name: str,
        notifier_manager: AbstractNotifierManager | None = None,
        result_store_manager: AbstractResultStoreManager | None = None,
        audit_store_manager: AbstractAuditStoreManager | None = None,
    ):
        if name in DataSentinelSession._active_sessions:
            raise SessionAlreadyExistsError(f"A session with name '{name}' already exists")
        self.name = name
        self._notifier_manager = notifier_manager or NotifierManager()
        self._result_store_manager = result_store_manager or ResultStoreManager()
        self._audit_store_manager = audit_store_manager or AuditStoreManager()
        DataSentinelSession._active_sessions[name] = self

    @property
    def _logger(self) -> logging.Logger:  # pragma: no cover
        return logging.getLogger(__name__)

    @classmethod
    def get_or_create(cls, name: str | None = None, **kwargs) -> "DataSentinelSession":
        """Get or create a new DataSentinel session

        Args:
            name: Name of session to be created or retrieved if a session exists with the
                same name
            **kwargs: Additional arguments passed to the DataSentinelSession constructor.

        Returns:
            The session created or retrieved
        """
        if name is None and len(cls._active_sessions) == 0:
            with cls._lock:
                return cls(str(ULID()), **kwargs)

        if name is None and len(cls._active_sessions) == 1:
            return next(iter(cls._active_sessions.values()))

        if name is None and len(cls._active_sessions) > 1:
            raise SessionNotSpecifiedError(
                "No name specified and there are multiple active sessions. Specify a name."
            )

        if name in cls._active_sessions:
            return cls._active_sessions[name]
        else:
            with cls._lock:
                return cls(name, **kwargs)

    @property
    def notifier_manager(self) -> AbstractNotifierManager:
        """Return the notifier manager"""
        return self._notifier_manager

    @property
    def result_store_manager(self) -> AbstractResultStoreManager:
        """Return the result store manager"""
        return self._result_store_manager

    @property
    def audit_store_manager(self) -> AbstractAuditStoreManager:
        """Return the audit store manager"""
        return self._audit_store_manager

    def run_validation_workflow(
        self,
        validation_workflow: ValidationWorkflow,
        runner: AbstractWorkflowRunner | None = None,
    ) -> None:
        """Runs a validation workflow.

        Args:
            validation_workflow: Validation workflow to run
            runner: Runner to be used to run the validation workflow
        """
        runner = runner or SimpleWorkflowRunner()
        runner.run(
            validation_workflow=validation_workflow,
            notifier_manager=self._notifier_manager,
            result_store_manager=self._result_store_manager,
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(name={self.name})"
