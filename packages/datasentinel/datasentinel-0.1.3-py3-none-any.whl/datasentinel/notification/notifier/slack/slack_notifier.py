from typing import Any

from slack_sdk import WebClient

from datasentinel.notification.notifier.core import AbstractNotifier, NotifierError
from datasentinel.notification.renderer.core import AbstractRenderer
from datasentinel.notification.renderer.slack.slack_message_renderer import SlackMessage
from datasentinel.validation.result import DataValidationResult


class SlackNotifier(AbstractNotifier):
    def __init__(
        self,
        name: str,
        channel: str,
        credentials: dict[str, Any],
        renderer: AbstractRenderer[SlackMessage],
        disabled: bool = False,
    ):
        super().__init__(name, disabled)
        if "SLACK_TOKEN" not in credentials:
            raise NotifierError("Slack token not found in credentials.")

        if not channel:
            raise NotifierError("Slack channel must be provided.")

        self._slack_token = credentials["SLACK_TOKEN"]
        self._channel = channel
        self._renderer = renderer

    def notify(self, result: DataValidationResult):
        message = self._renderer.render(result)
        try:
            client = WebClient(token=self._slack_token)
            client.chat_postMessage(
                channel=self._channel, blocks=message.blocks, text=message.text
            )
        except Exception as e:
            raise NotifierError(f"Error while sending slack message: {e!s}") from e
