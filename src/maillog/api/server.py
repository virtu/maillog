"""Maillog functionality for handling client requests."""

import datetime as dt
import json
import logging as log
import os
import socket
import threading
from dataclasses import dataclass

from maillog.message import Message, MessageBuffer

from .socket import APISocket


@dataclass
class APIServer(threading.Thread):
    """Handlers for client requests."""

    buffer: MessageBuffer
    api_socket: APISocket = APISocket.listen()

    def __hash__(self):
        """Class must be hashable for threading.Thread."""
        return hash(self.api_socket)

    def __post_init__(self):
        """Initialize the parent class."""
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
            log.debug("Trying to read data from socket...")
            msg = client_socket.receive()
            action = msg.get("action")
            if action == "send":
                log.debug("Received send request.")
                # self.handle_send(request, client_socket)
            elif action == "status":
                log.debug("Received status request.")
                # self.handle_status(client_socket)
            else:
                log.warning("Unknown action: %s", action)
        finally:
            client_socket.close()

    def handle_send(self, request: dict, client_socket: socket.socket):
        """Handle send request from client."""
        timestamp = dt.datetime.now(dt.timezone.utc)
        msg = str(request.get("msg"))
        immediate = request.get("immediate", False)
        log_level = request.get("log_level", "warning")
        process_name = request.get("process_name", "unknown")
        process_id = request.get("process_id", "unknown")

        log_func = getattr(log, log_level, log.warning)
        log_func(f"[{process_name}][{process_id}] {msg} (logging from maillog)")

        message = Message(
            timestamp=timestamp,
            process_name=process_name,
            process_id=process_id,
            message=msg,
            log_level=log_level,
        )

        if immediate:
            print("TODO: implement")
            # subject = f"maillog: urgent message from {process_name} on {self.hostname}"
            # content = f"[{timestamp}] [{log_level}] {msg}\nProcess: {process_name}\nPID: {process_id}"
            # self.send_email(subject, content)
        else:
            self.buffer.insert(message)

        client_socket.sendall(json.dumps({"status": "ok"}).encode("utf-8"))

    def handle_status(self, client_socket: socket.socket):
        """
        Handle status request from client.

        Since grouping and formatting messages is handled by the client, the
        server can simply return the buffered messages.
        """
        response = self.buffer.get_all_messages()
        client_socket.sendall(json.dumps(response).encode("utf-8"))
