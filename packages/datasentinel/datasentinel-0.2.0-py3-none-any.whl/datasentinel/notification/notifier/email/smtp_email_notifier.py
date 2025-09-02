"""SMTP email notifier."""

from email.message import EmailMessage
from smtplib import SMTP
from typing import Any

from datasentinel.notification.notifier.core import AbstractNotifier, NotifierError
from datasentinel.notification.renderer.core import AbstractRenderer
from datasentinel.validation.result import DataValidationResult


class SMTPEmailNotifier(AbstractNotifier):
    """SMTP email notifier."""

    def __init__(  # noqa PLR0913
        self,
        name: str,
        server: str,
        port: int,
        domain: str,
        renderer: AbstractRenderer[EmailMessage],
        credentials: dict[str, Any],
        mail_rcp: list[str] | None = None,
        mail_rcp_cc: list[str] | None = None,
        use_tls: bool = True,
        disabled: bool = False,
    ):
        super().__init__(name, disabled)
        self._server = server
        self._port = port
        self._mail_rcp = mail_rcp if mail_rcp else []
        self._mail_rcp_cc = mail_rcp_cc if mail_rcp_cc else []
        self._domain = domain
        self._renderer = renderer
        self._use_tls = use_tls

        if "username" not in credentials or "password" not in credentials:
            raise NotifierError("Username or password not found in credentials.")

        self._username = credentials["username"]
        self._password = credentials["password"]

    def _define_recipients(self, message: EmailMessage):
        message["From"] = self._username
        message["To"] = ", ".join(self._mail_rcp)
        message["BCC"] = ", ".join(self._mail_rcp)
        if self._mail_rcp_cc:
            message["CC"] = ", ".join(self._mail_rcp_cc)

        return message

    def notify(self, result: DataValidationResult):
        """Send a notification using SMTP protocol."""
        message = self._define_recipients(self._renderer.render(result))
        try:
            with SMTP(self._server, self._port) as server:
                server.ehlo(self._domain)
                if self._use_tls:
                    server.starttls()
                    server.ehlo(self._domain)
                    server.login(self._username, self._password)
                server.send_message(message)
                server.quit()
        except Exception as e:
            raise NotifierError(f"Error while sending email: {e!s}") from e
