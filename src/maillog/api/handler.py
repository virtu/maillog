"""Maillog server functionality for handling client requests."""

import logging as log

from maillog.event import EventBuffer

from . import messages
from .socket import APISocket


class RequestHandler:
    """API call handlers for client requests."""

    @staticmethod
    def handle_request(client_socket: APISocket):
        """Handle incoming client requests."""
        log.debug("Received client request (socket: %s)", client_socket)
        try:
            log.debug("Reading APIMessage from socket.")
            msg = client_socket.receive()
            if isinstance(msg, messages.APISubmitEventRequest):
                log.debug("Received submit request.")
                RequestHandler.handle_submit(msg, client_socket)
            elif isinstance(msg, messages.APIGetStatusRequest):
                log.debug("Received status request.")
                RequestHandler.handle_status(client_socket)
            else:
                log.warning("Unsupported API message: %s", msg)
        finally:
            client_socket.close()

    @staticmethod
    def handle_submit(
        request: messages.APISubmitEventRequest,
        client_socket: APISocket,
    ):
        """Handle send request from client."""

        event = request.event
        log.debug("Received APISubmitEventRequest with event %s", event)
        with EventBuffer() as buf:
            buf.insert(event)
        log.info('Received event from client (preview: "%s")', event.message[:20])

        response = messages.APISubmitEventResponse(success=True)
        client_socket.send(response)

    @staticmethod
    def handle_status(client_socket: APISocket):
        """
        Handle status request from client.

        Since grouping and formatting messages is handled by the client, the
        server can simply return the buffered messages.
        """
        with EventBuffer() as buf:
            events = buf.get_all_events()
        log.info("Received status request from client. Sending %d events.", len(events))
        response = messages.APIGetStatusResponse(success=True, events=events)
        client_socket.send(response)
