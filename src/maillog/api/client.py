"""Module implementing API client interface."""

import logging as log

from maillog.event import MaillogEvent

from .messages import APISubmitEventRequest
from .socket import APISocket


def info(msg: str):
    """Log message via regular logging framework and maillog using info level."""
    log.info(msg)
    _send(msg, "INFO")


def warning(msg: str):
    """Log message via regular logging framework and maillog using warning level."""
    log.warning(msg)
    _send(msg, "WARNING")


def error(message: str):
    """Log message via regular logging framework and maillog using warning level."""
    log.warning(message)
    _send(message, "WARNING")


def _send(msg: str, log_level: str):
    """Create log event from message and send to maillog server."""

    event = MaillogEvent(msg, log_level)
    request = APISubmitEventRequest(event)
    api_socket = APISocket.connect()
    api_socket.send(request)
    # TODO: wait for response
