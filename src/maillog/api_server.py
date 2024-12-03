"""Maillog functionality for handling client requests."""

import datetime as dt
import json
import logging as log
import os
import socket
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from maillog.message import Message, MessageBuffer


@dataclass(unsafe_hash=True)
class APIServer(threading.Thread):
    """Handlers for client requests."""

    buffer: MessageBuffer
    api_socket: socket.socket = field(init=False)
    SOCKET_READ_SIZE: ClassVar[int] = 4096
    SOCKET_PATH: ClassVar[str] = "/run/maillog/server_socket"

    def __post_init__(self):
        """Initialize the parent class."""
        super().__init__(name=self.__class__.__name__)

    def run(self):
        """
        Start the API server.

        This function is called by the Threading class's start method.
        """
        self.setup_socket()
        self.server_loop()

    def server_loop(self):
        """Listen for incoming client requests."""
        try:
            while True:
                client_socket, _ = self.api_socket.accept()
                threading.Thread(
                    target=self.handle_client_request, args=(client_socket,)
                ).start()
        finally:
            self.api_socket.close()
            if os.path.exists(self.SOCKET_PATH):
                os.remove(self.SOCKET_PATH)

    def setup_socket(self):
        """Set up the API socket."""
        socket_path = Path(self.SOCKET_PATH)
        if socket_path.exists():
            log.debug("Removed existing socket (%s)", self.SOCKET_PATH)
            socket_path.unlink()
        self.api_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.api_socket.bind(self.SOCKET_PATH)
        os.chmod(self.SOCKET_PATH, 0o666)
        log.debug("Created socket (%s)", self.SOCKET_PATH)

    def handle_client_request(self, client_socket: socket.socket):
        """Handle incoming client requests."""
        try:
            data = ""
            while True:
                chunk = client_socket.recv(APIServer.SOCKET_READ_SIZE)
                if not chunk:
                    break
                data += chunk.decode("utf-8")
            if data:
                request = json.loads(data)
                action = request.get("action")
                if action == "send":
                    self.handle_send(request, client_socket)
                elif action == "status":
                    self.handle_status(client_socket)
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
        response = self.buffer.get_all()
        client_socket.sendall(json.dumps(response).encode("utf-8"))
