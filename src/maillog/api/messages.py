"""Module for API message classes."""

import logging as log
import pickle
from dataclasses import dataclass
from typing import ClassVar

from maillog.event import MaillogEvent


@dataclass
class APIMessage:
    """Class representing messages sent and received via the APISocket class."""

    FRAME_PREFIX_LENGTH: ClassVar[int] = 4

    def to_frame(self) -> bytes:
        """Convert the message to a frame (wire format)."""
        payload = pickle.dumps(self)
        length = len(payload)
        log.debug(
            "Encoding %s to frame of length %d (payload=%s)", self, length, payload
        )
        frame = length.to_bytes(self.FRAME_PREFIX_LENGTH, byteorder="big") + payload
        return frame

    @classmethod
    def from_payload(cls, payload: bytes) -> "APIMessage":
        """Convert a message frame to an API message."""
        return pickle.loads(payload)


@dataclass
class APISubmitEventRequest(APIMessage):
    """Class representing a request to submit a maillog event."""

    event: MaillogEvent


@dataclass
class APISubmitEventResponse(APIMessage):
    """Class representing a response to a event-submission request."""

    success: bool


@dataclass
class APIGetStatusRequest(APIMessage):
    """Class representing a request get the status of the maillog server."""


@dataclass
class APIGetStatusResponse(APIMessage):
    """Class representing a response to a status request."""

    success: bool
    events: list[MaillogEvent]


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
