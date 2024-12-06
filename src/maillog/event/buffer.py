"""Module implementing message and message buffer classes."""

import json
import logging as log
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, List

from .event import MaillogEvent


@dataclass
class EventBuffer:
    """Buffer for storing log messages."""

    _lock: threading.Lock = threading.Lock()
    _event_buffer: List = field(init=False)
    # TODO: revert to "/run/maillog/message_buffer.json"
    BUFFER_FILE: ClassVar[Path] = Path("message_buffer.json")

    def __post_init__(self):
        """Initialize event buffer from file if it exists."""
        if not self.BUFFER_FILE.exists():
            self._data = []
            return
        with self.BUFFER_FILE.open("r", encoding="UTF-8") as f:
            self._data = json.load(f)
            log.info(
                "Restored %d message(s) from file (%s)",
                len(self._event_buffer),
                self.BUFFER_FILE,
            )

    def _persist(self):
        """Persist buffer to disk."""
        with open(self.BUFFER_FILE, "w", encoding="UTF-8") as f:
            json.dump(self._event_buffer, f)

    def insert(self, event: MaillogEvent):
        """Add a message to the buffer and persist buffer to disk."""
        with self._lock:
            self._event_buffer.append(event)
            self._persist()

    def get_all_messages(self):
        """Get all messages from the buffer."""
        with self._lock:
            return self._event_buffer

    def clear(self):
        """Clear the buffer and persist to disk."""
        with self._lock:
            self._event_buffer = []
            self._persist()
