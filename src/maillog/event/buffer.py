"""Module implementing message and message buffer classes."""

import logging as log
import pickle
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from .event import MaillogEvent


@dataclass
class EventBuffer:
    """Buffer for storing log messages."""

    _lock: threading.Lock = threading.Lock()
    _event_buffer: list = field(init=False)
    # TODO: revert to "/run/maillog/message_buffer.pickle"
    BUFFER_FILE: ClassVar[Path] = Path("message_buffer.pickle")

    def __post_init__(self):
        """Initialize event buffer from file if it exists."""
        if not self.BUFFER_FILE.exists():
            self._event_buffer = []
            return
        with self.BUFFER_FILE.open("rb") as f:
            self._event_buffer = pickle.load(f)
            log.info(
                "Restored %d message(s) from file (%s)",
                len(self._event_buffer),
                self.BUFFER_FILE,
            )

    def _persist(self):
        """Persist buffer to disk."""
        with open(self.BUFFER_FILE, "wb") as f:
            pickle.dump(self._event_buffer, f)
            num_events = len(self._event_buffer)
            log.debug(
                "Persisted %s event(s) to disk (%s)", num_events, self.BUFFER_FILE
            )

    def insert(self, event: MaillogEvent):
        """Add a message to the buffer and persist buffer to disk."""
        with self._lock:
            self._event_buffer.append(event)
            num_events = len(self._event_buffer)
            log.debug(
                "Added event to buffer (before=%d, after=%d)",
                num_events - 1,
                num_events,
            )
            self._persist()

    def get_all_events(self):
        """Get all events from the buffer."""
        with self._lock:
            num_events = len(self._event_buffer)
            log.debug(
                "Fetched %s event(s) from buffer",
                num_events,
            )
            return self._event_buffer

    def clear(self):
        """Clear the buffer and persist to disk."""
        with self._lock:
            num_events = len(self._event_buffer)
            log.debug(
                "Cleared buffer (removed %d event(s))",
                num_events,
            )
            self._event_buffer = []
            self._persist()
