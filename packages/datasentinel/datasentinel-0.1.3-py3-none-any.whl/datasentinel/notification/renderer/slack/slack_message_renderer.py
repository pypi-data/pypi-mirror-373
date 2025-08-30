from pydantic.dataclasses import dataclass

from datasentinel.notification.renderer.core import AbstractRenderer, RendererError
from datasentinel.validation.result import DataValidationResult
from datasentinel.validation.rule.metric import RuleMetric
from datasentinel.validation.status import Status


@dataclass
class SlackMessage:
    text: str
    blocks: list[dict]


class SlackMessageRenderer(AbstractRenderer[SlackMessage]):
    _FAILED_CHECKS_DISPLAY_LIMIT = 5
    _FAILED_RULES_DISPLAY_LIMIT = 5

    def __init__(self, checks_display_limit: int = 3, rules_display_limit: int = 5):
        if not 0 < checks_display_limit <= self._FAILED_CHECKS_DISPLAY_LIMIT:
            raise RendererError("Checks display limit must be greater than 0 and less than 5.")
        if not 0 < rules_display_limit <= self._FAILED_RULES_DISPLAY_LIMIT:
            raise RendererError("Rules display limit must be greater than 0 and less than 5.")
        self._checks_display_limit = checks_display_limit
        self._rules_display_limit = rules_display_limit

    def _render_text_rules_metric(self, rules_metric: list[RuleMetric]) -> str:
        return ", ".join(
            [
                f"[{self._render_rule_metric_info(rule_metric)}]"
                for rule_metric in rules_metric[: self._rules_display_limit]
            ]
        )

    def _render_text_message(self, result: DataValidationResult) -> str:
        status = result.status
        status_str = "passed" if status == Status.PASS else "failed"
        message = (
            f"{result.name} data validation {status_str}!, run id: {result.run_id}, "
            f"data asset: {result.data_asset}, "
            f"data asset schema: {result.data_asset_schema}, "
            f"start time: {result.start_time.isoformat()}, "
            f"end time: {result.end_time.isoformat()}."
        )

        if status == Status.PASS:
            return message

        failed_checks_str = ", ".join(
            [
                (
                    f"{failed_check.name} "
                    f"({self._render_text_rules_metric(failed_check.failed_rules)})"
                )
                for failed_check in result.failed_checks[: self._checks_display_limit]
            ]
        )

        return f"{message} Failed checks: {failed_checks_str}"

    @staticmethod
    def _render_rule_metric_info(rule_metric: RuleMetric) -> str:
        _value_or_col = (
            f"column: [{', '.join(rule_metric.column or [])}]"
            if not rule_metric.rule == "is_custom"
            else f"value: {rule_metric.value}"
        )

        return (
            f"id: {rule_metric.id}, rule: {rule_metric.rule}, {_value_or_col}, "
            f"evaluated rows: {rule_metric.rows}, violations: {rule_metric.violations}"
        )

    def _render_rules_metric_blocks(self, rules_metric: list[RuleMetric]) -> list[dict]:
        return [
            {
                "type": "rich_text_section",
                "elements": [
                    {"type": "text", "text": self._render_rule_metric_info(rule_metric)}
                ],
            }
            for rule_metric in rules_metric[: self._rules_display_limit]
        ]

    def _render_blocks_message(self, result: DataValidationResult) -> list[dict]:
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": (
                        "A data validation has passed! :white_check_mark:"
                        if result.status == Status.PASS
                        else "A data validation has failed! :alerta:"
                    ),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(
                        [
                            f"*Name:* {result.name}",
                            f"*Run ID*: {result.run_id}",
                            f"*Data Asset*: {result.data_asset}",
                            (
                                f"*Data Asset Schema*: {result.data_asset_schema}"
                                if result.data_asset_schema
                                else ""
                            ),
                            f"*Start Time*: {result.start_time.isoformat()}",
                            f"*End Time*: {result.end_time.isoformat()}",
                        ]
                    ),
                },
            },
        ]

        if result.status == Status.PASS:
            return blocks
        blocks.append({"type": "divider"})
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Failed Checks* "
                        f"(Showing only {self._checks_display_limit} "
                        f"of {result.failed_checks_count}):"
                        if result.failed_checks_count > self._checks_display_limit
                        else "*Failed Checks*:"
                    ),
                },
            }
        )

        blocks.extend(
            [
                {
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Check name: ",
                                    "style": {"bold": True},
                                },
                                {
                                    "type": "text",
                                    "text": failed_check.name,
                                },
                            ],
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Check level: ",
                                    "style": {"bold": True},
                                },
                                {"type": "text", "text": failed_check.level.name},
                            ],
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": (
                                        f"Failed rules "
                                        f"(Showing only {self._rules_display_limit} "
                                        f"of {failed_check.failed_rules_count}): "
                                        if (
                                            failed_check.failed_rules_count
                                            > self._rules_display_limit
                                        )
                                        else "Failed rules: "
                                    ),
                                    "style": {"bold": True},
                                }
                            ],
                        },
                        {
                            "type": "rich_text_list",
                            "style": "bullet",
                            "indent": 0,
                            "elements": [
                                *self._render_rules_metric_blocks(failed_check.failed_rules)
                            ],
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "  ",
                                }
                            ],
                        },
                    ],
                }
                for failed_check in result.failed_checks[: self._checks_display_limit]
            ]
        )

        return blocks

    def render(self, result: DataValidationResult) -> SlackMessage:
        return SlackMessage(
            text=self._render_text_message(result),
            blocks=self._render_blocks_message(result),
        )
