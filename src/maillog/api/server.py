"""Maillog server functionality for handling client requests."""

import logging as log
import threading
from dataclasses import dataclass, field

from .handler import RequestHandler
from .socket import APISocket


@dataclass
class APIServer(threading.Thread):
    """API Server class along with handlers for client requests."""

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
                target=RequestHandler.handle_request,
                args=(client_socket,),
            ).start()
