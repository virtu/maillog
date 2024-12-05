"""Module for API message classes."""

import pickle
from dataclasses import dataclass


@dataclass
class APIMessage:
    """Class representing messages sent and received via the APISocket class."""

    command: str


@dataclass
class APIMessageFrame:
    """
    Class representing message sent via sockets.

    Includes a length prefix to ensure reliable message transmission.
    """

    length: bytes
    message: bytes

    @classmethod
    def from_api_message(cls, message: APIMessage) -> "APIMessageFrame":
        """Create a message frame from an API message."""
        message_bytes = pickle.dumps(message)
        length_bytes = len(message_bytes).to_bytes(4, byteorder="big")
        return cls(length_bytes, message_bytes)

    def decode(self) -> APIMessage:
        """Decode the message frame into an API message."""
        return pickle.loads(self.message)
