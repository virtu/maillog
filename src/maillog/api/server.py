"""Maillog server functionality for handling client requests."""

import logging as log
import threading
from dataclasses import dataclass, field

from maillog.event import EventBuffer

from . import messages
from .socket import APISocket


@dataclass
class APIServer(threading.Thread):
    """API Server class along with handlers for client requests."""

    event_buffer: EventBuffer
    api_socket: APISocket = field(init=False)

    def __hash__(self):
        """Class must be hashable for threading.Thread."""
        return hash(self.__class__.__name__)

    def __post_init__(self):
        """Initialize the parent class."""
        self.api_socket = APISocket.listen()
        super().__init__(name=self.__class__.__name__)

    def run(self):
        """
        Start the API server.

        This function is called by the Threading class's start method.
        """
        log.info("Started %s thread.", self.__class__.__name__)
        while True:
            client_socket = self.api_socket.accept()
            threading.Thread(
                target=self.handle_client_request, args=(client_socket,)
            ).start()

    def handle_client_request(self, client_socket: APISocket):
        """Handle incoming client requests."""
        log.debug("Received client request (socket: %s)", client_socket)
        try:
            log.debug("Reading APIMessage from socket.")
            msg = client_socket.receive()
            if isinstance(msg, messages.APISubmitEventRequest):
                log.debug("Received submit request.")
                self.handle_submit(msg, client_socket)
            elif isinstance(msg, messages.APIGetStatusRequest):
                log.debug("Received status request.")
                self.handle_status(client_socket)
            else:
                log.warning("Unsupported API message: %s", msg)
        finally:
            client_socket.close()

    def handle_submit(
        self, request: messages.APISubmitEventRequest, client_socket: APISocket
    ):
        """Handle send request from client."""

        event = request.event
        log.debug("Received APISubmitEventRequest with event %s", event)
        self.event_buffer.insert(event)

        response = messages.APISubmitEventResponse(success=True)
        client_socket.send(response)

    def handle_status(self, client_socket: APISocket):
        """
        Handle status request from client.

        Since grouping and formatting messages is handled by the client, the
        server can simply return the buffered messages.
        """
        events = self.event_buffer.get_all_events()
        response = messages.APIGetStatusResponse(success=True, events=events)
        client_socket.send(response)
