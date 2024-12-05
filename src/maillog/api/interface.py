"""Module defining API call interface."""

import logging as log


def info(message: str):
    """Log message via regular logging framework and maillog using info level."""
    log.info(message)
    _send(message, "INFO")


def _send(messsage: str, log_level: str):
    """
    Send message to maillog server.

    Create MaillogMessage object, then send it to the maillog server API.
    """

    maillog_message = MaillogMessage(message, log_level)
