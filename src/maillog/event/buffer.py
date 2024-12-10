"""Module implementing message and message buffer classes."""

import logging as log
import pickle
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from .event import MaillogEvent


@dataclass
class EventBuffer:
    """Buffer for storing log messages."""

    BUFFER_LOCK: ClassVar[threading.Lock] = threading.Lock()
    BUFFER_FILE: ClassVar[Path] = Path("/var/lib/maillog/message_buffer.pickle")

    def __enter__(self):
        """Acquire the buffer lock."""
        self.BUFFER_LOCK.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release the buffer lock."""
        self.BUFFER_LOCK.release()

    def _read_events(self) -> list[MaillogEvent]:
        """Read events from the file."""
        if not self.BUFFER_FILE.exists():
            return []
        with self.BUFFER_FILE.open("rb") as f:
            events = pickle.load(f)
            return events

    def _write_events(self, events: list[MaillogEvent]):
        """Write events to the file."""
        with self.BUFFER_FILE.open("wb") as f:
            pickle.dump(events, f)
        log.debug("Persisted %d event(s) to disk (%s)", len(events), self.BUFFER_FILE)

    def insert(self, event: MaillogEvent):
        """Add a message to the buffer and persist."""
        events = self._read_events()
        before_count = len(events)
        events.append(event)
        after_count = len(events)
        log.debug(
            "Added event to buffer (before=%d, after=%d)",
            before_count,
            after_count,
        )
        self._write_events(events)

    def get_all_events(self) -> list[MaillogEvent]:
        """Get all events from the buffer."""
        events = self._read_events()
        log.debug("Fetched %d event(s) from buffer", len(events))
        return events

    def clear(self):
        """Clear the buffer and persist."""
        events = self._read_events()
        num_events = len(events)
        log.debug("Cleared buffer (removed %d event(s))", num_events)
        self._write_events([])
