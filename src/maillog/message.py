"""Module implementing message and message buffer classes."""

import datetime as dt
import json
import logging as log
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, List


@dataclass
class Message:
    """Class representing log messages."""

    timestamp: dt.datetime
    process_name: str
    process_id: int
    message: str
    log_level: str


@dataclass
class MessageBuffer:
    """Buffer for storing log messages."""

    lock: threading.Lock = threading.Lock()
    data: List = field(init=False)
    BUFFER: ClassVar[str] = "/run/maillog/message_buffer.json"

    def __post_init__(self):
        """Try to load buffered data from file."""
        buffer_path = Path(self.BUFFER)
        if not buffer_path.exists():
            self.data = []
        with buffer_path.open("r", encoding="UTF-8") as f:
            self.data = json.load(f)
            log.info("Read %d messages from disk (%s)", len(self.data), self.BUFFER)

    def persist(self):
        """Persist buffer to disk."""
        with open(self.BUFFER, "w", encoding="UTF-8") as f:
            json.dump(self.data, f)

    def insert(self, message: Message):
        """Add a message to the buffer and persist buffer to disk."""
        with self.lock:
            self.data.append(message)
            self.persist()

    def get_all(self):
        """Get all messages from the buffer."""
        with self.lock:
            return self.data

    def clear(self):
        """Clear the buffer and persist to disk."""
        with self.lock:
            self.data = []
            self.persist()
