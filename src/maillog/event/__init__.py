"""Module for maillog event and buffer classes."""

from .buffer import EventBuffer
from .event import MaillogEvent

__all__ = ["MaillogEvent", "EventBuffer"]
