import logging

from datasentinel.notification.notifier.core import AbstractNotifierManager
from datasentinel.store.result.core import AbstractResultStoreManager
from datasentinel.validation.check.level import CheckLevel
from datasentinel.validation.check.result import CheckResult
from datasentinel.validation.result import DataValidationResult
from datasentinel.validation.runner.core import AbstractWorkflowRunner, CriticalCheckFailedError
from datasentinel.validation.status import Status
from datasentinel.validation.workflow import ValidationWorkflow


class SimpleWorkflowRunner(AbstractWorkflowRunner):
    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    def run(
        self,
        validation_workflow: ValidationWorkflow,
        notifier_manager: AbstractNotifierManager,
        result_store_manager: AbstractResultStoreManager,
    ) -> None:
        """Run a data validation workflow."""
        data_validation_result = validation_workflow.data_validation.run()

        self._log_status(result=data_validation_result)

        notifier_manager.notify_all_by_event(
            notifiers_by_events=validation_workflow.notifiers_by_event,
            result=data_validation_result,
        )
        result_store_manager.store_all(
            result_stores=validation_workflow.result_stores, result=data_validation_result
        )

        self._raise_exc_on_failed_critical_checks(result=data_validation_result)

    def _log_status(self, result: DataValidationResult) -> None:
        data_asset_info = (
            f"Data asset '{result.data_asset}' in schema '{result.data_asset_schema}'"
            if result.data_asset_schema is not None
            else f"Data asset '{result.data_asset}'"
        )

        if result.status == Status.PASS:
            self._logger.info(
                f"{data_asset_info} passed all checks on data validation '{result.name}'"
            )
            return

        _logger_methods_map = {
            CheckLevel.WARNING: self._logger.warning,
            CheckLevel.ERROR: self._logger.error,
            CheckLevel.CRITICAL: self._logger.critical,
        }

        for level, method in _logger_methods_map.items():
            failed_checks = result.failed_checks_by_level(level)
            if not failed_checks:
                continue

            summary = self._failed_checks_summary(result.failed_checks_by_level(level))
            method(
                f"{data_asset_info} failed checks: {summary} on data validation '{result.name}'"
            )

    @staticmethod
    def _failed_checks_summary(failed_checks: list[CheckResult]) -> str:
        failed_checks_str = []
        for failed_check in failed_checks:
            failed_rules_str = ", ".join(
                [
                    f"{rule_metric.rule}[column: {rule_metric.column}]"
                    if rule_metric.column is not None
                    else rule_metric.rule
                    for rule_metric in failed_check.failed_rules
                ]
            )
            failed_checks_str.append(f"{failed_check.name}({failed_rules_str})")

        return ", ".join(failed_checks_str)

    def _raise_exc_on_failed_critical_checks(self, result: DataValidationResult) -> None:
        critical_failed_checks = result.failed_checks_by_level(CheckLevel.CRITICAL)
        if critical_failed_checks:
            summary = self._failed_checks_summary(critical_failed_checks)
            data_asset_info = (
                f"Data asset '{result.data_asset}' in schema '{result.data_asset_schema}'"
                if result.data_asset_schema is not None
                else f"Data asset '{result.data_asset}'"
            )
            raise CriticalCheckFailedError(
                f"{data_asset_info} failed checks: {summary} on data validation '{result.name}'"
            )
