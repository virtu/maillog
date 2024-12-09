"""Module containing emailing-sending functionality."""

import logging as log
import smtplib
from dataclasses import dataclass
from email.mime.text import MIMEText

from maillog.cli.maillogd import EmailConfig


@dataclass
class Mailer:
    """Class for high-level email sending functionality."""

    config: EmailConfig

    def send(self, subject: str, body: str):
        """Send email with given subject and content."""

        message = MIMEText(body, "plain")
        message["From"] = self.config.from_
        message["To"] = self.config.to
        message["Subject"] = subject

        with smtplib.SMTP(self.config.server, self.config.port) as server:
            server.starttls()
            server.login(self.config.username, self.config.password)
            server.sendmail(self.config.from_, self.config.to, message.as_string())
            log.info(
                "Email sent successfully (from=%s, to=%s, subject=%s)",
                self.config.from_,
                self.config.to,
                subject,
            )
