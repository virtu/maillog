"""Module implementing message and message buffer classes."""

import datetime as dt
import json
import logging as log
import os
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, List


@dataclass
class Message:
    """
    Class representing log messages.

    Process name and id don't change, so they can be set once and shared across
    all instances. Timestamp is set for each instance individually, so it uses
    a default_factory.
    """

    message: str
    immediate: bool
    log_level: str
    process_name: str = field(init=False, default=os.path.basename(sys.argv[0]))
    process_id: int = field(init=False, default=os.getpid())
    timestamp: str = field(
        init=False,
        default_factory=lambda: dt.datetime.now(dt.timezone.utc).isoformat(
            timespec="seconds"
        ),
    )


@dataclass
class MessageBuffer:
    """Buffer for storing log messages."""

    _lock: threading.Lock = threading.Lock()
    _data: List = field(init=False)
    # BUFFER: ClassVar[str] = "/run/maillog/message_buffer.json"
    BUFFER: ClassVar[str] = "message_buffer.json"

    def __post_init__(self):
        """Try to load buffered data from file."""
        buffer_path = Path(self.BUFFER)
        if not buffer_path.exists():
            self._data = []
            return
        with buffer_path.open("r", encoding="UTF-8") as f:
            self._data = json.load(f)
            log.info("Read %d messages from disk (%s)", len(self._data), self.BUFFER)

    def _persist(self):
        """Persist buffer to disk."""
        with open(self.BUFFER, "w", encoding="UTF-8") as f:
            json.dump(self._data, f)

    def insert(self, message: Message):
        """Add a message to the buffer and persist buffer to disk."""
        with self._lock:
            self._data.append(message)
            self._persist()

    def get_all_messages(self):
        """Get all messages from the buffer."""
        with self._lock:
            return self._data

    def clear(self):
        """Clear the buffer and persist to disk."""
        with self._lock:
            self._data = []
            self._persist()
