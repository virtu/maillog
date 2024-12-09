"""Maillog functionality for handling client requests."""

import logging as log
import os
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from .messages import APIMessage


@dataclass
class APISocket:
    """High-level API server class implementing low-level socket handling."""

    _socket: socket.socket
    # TODO: Revert to "/run/maillog/server_socket"
    SOCKET_PATH: ClassVar[str] = "server_socket"
    SOCKET_TIMEOUT: ClassVar[int] = 5

    @classmethod
    def connect(cls):
        """Connect to the API server."""
        api_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        api_socket.connect(cls.SOCKET_PATH)
        api_socket.settimeout(cls.SOCKET_TIMEOUT)
        return cls(_socket=api_socket)

    @classmethod
    def listen(cls):
        """Create an API socket."""
        socket_path = Path(APISocket.SOCKET_PATH)
        if socket_path.exists():
            log.debug("Removed existing socket (%s)", APISocket.SOCKET_PATH)
            socket_path.unlink()
        api_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        api_socket.bind(APISocket.SOCKET_PATH)
        os.chmod(APISocket.SOCKET_PATH, 0o666)
        log.debug("Created socket (%s)", APISocket.SOCKET_PATH)
        api_socket.listen()
        return cls(_socket=api_socket)

    def accept(self):
        """Accept connection from client."""
        conn, _ = self._socket.accept()
        return APISocket(_socket=conn)

    def close(self):
        """Close socket."""
        self._socket.close()

    def send(self, message: APIMessage):
        """Send API message to the API socket."""
        self._socket.sendall(message.to_frame())

    def receive(self) -> APIMessage:
        """
        Receive data from API socket.

        Read frame prefix, then read appropriate amount of bytes to get entire
        payload of the frame. Create APIMessage from payload and return
        message.
        """
        pfx_bytes = self._socket.recv(APIMessage.FRAME_PREFIX_LENGTH)
        pfx = int.from_bytes(pfx_bytes, "big")
        log.debug("Frame payload length per prefix: %s byte(s)", pfx)
        payload = self._socket.recv(pfx)
        msg = APIMessage.from_payload(payload)
        log.debug("Received message: %s", msg)
        return msg
