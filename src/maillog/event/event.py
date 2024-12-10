"""Module implementing message and message buffer classes."""

import datetime as dt
import os
import sys
from dataclasses import dataclass, field


@dataclass
class MaillogEvent:
    """
    Class representing a maillog event.

    Use default_factory for all fields to ensure the values don't use the
    maillogd binaries process name, id and timestamp.
    """

    message: str
    log_level: str
    process_name: str = field(
        init=False, default_factory=lambda: os.path.basename(sys.argv[0])
    )
    process_id: int = field(init=False, default_factory=lambda: os.getpid())
    timestamp: str = field(
        init=False,
        default_factory=lambda: dt.datetime.strftime(
            dt.datetime.now(dt.timezone.utc), "%Y-%m-%dT%H:%M:%SZ"
        ),
    )
