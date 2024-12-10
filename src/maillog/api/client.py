"""Module implementing API client interface."""

import logging as log

from maillog.event import EventFormatter, MaillogEvent

from . import messages
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
    """Log message via regular logging framework and maillog using error level."""
    log.error(message)
    _send(message, "ERROR")


def _send(msg: str, log_level: str):
    """Create log event from message and send it to the maillog server."""
    event = MaillogEvent(msg, log_level)
    request = messages.APISubmitEventRequest(event)
    api_socket = APISocket.connect()
    api_socket.send(request)
    response = api_socket.receive()
    log.debug(response)


def get_status():
    """Get status of the server."""
    request = messages.APIGetStatusRequest()
    api_socket = APISocket.connect()
    api_socket.send(request)
    response = api_socket.receive()
    assert isinstance(
        response, messages.APIGetStatusResponse
    ), "Unexpected response type"
    if not response.success:
        raise ValueError(response)
    num_events = len(response.events)
    log.info("GetStatus: Received %d events", num_events)
    if num_events > 0:
        log.info("Event list:\n%s", EventFormatter.pretty_print(response.events))
