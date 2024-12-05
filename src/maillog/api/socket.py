"""Maillog functionality for handling client requests."""

import json
import logging as log
import os
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass
class APISocket:
    """High-level API server class implementing low-level socket handling."""

    _socket: socket.socket
    # SOCKET_PATH: ClassVar[str] = "/run/maillog/server_socket"
    SOCKET_PATH: ClassVar[str] = "server_socket"
    MSG_LEN_PFX_SIZE: ClassVar[int] = 4  # size of message length prefix

    @classmethod
    def connect(cls):
        """Connect to the API server."""
        api_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        api_socket.connect(cls.SOCKET_PATH)
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

    def send(self, data: dict):
        """
        Send data to the API socket.

        Convert JSON data to bytes, then calculate message length. Finally,
        send message length as prefix followed by message.
        """
        msg = json.dumps(data)
        msg_bytes = msg.encode("utf-8")
        msg_len = len(msg_bytes)
        msg_len_bytes = msg_len.to_bytes(self.MSG_LEN_PFX_SIZE, "big")
        log.debug("Sending message (msg=%s, len=%s)", msg, msg_len)
        self._socket.sendall(msg_len_bytes + msg_bytes)

    def receive(self) -> dict:
        """
        Receive data from API socket.

        Read message length prefix, then read message. Return decoded message.
        """
        msg_len_bytes = self._socket.recv(self.MSG_LEN_PFX_SIZE)
        msg_len = int.from_bytes(msg_len_bytes, "big")
        log.debug("Received message length: %s byte(s)", msg_len)
        msg_bytes = self._socket.recv(msg_len)
        msg = json.loads(msg_bytes.decode("utf-8"))
        log.debug("Received message: %s", msg)
        return msg
