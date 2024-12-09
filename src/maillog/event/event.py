"""Module implementing message and message buffer classes."""

import datetime as dt
import os
import sys
from dataclasses import dataclass, field


@dataclass
class MaillogEvent:
    """
    Class representing a maillog event.

    Process name and id don't change, so they can be set once and shared across
    all instances. Timestamp is set for each instance individually, so a
    default_factory is necessary.
    """

    message: str
    log_level: str
    process_name: str = field(init=False, default=os.path.basename(sys.argv[0]))
    process_id: int = field(init=False, default=os.getpid())
    timestamp: str = field(
        init=False,
        default_factory=lambda: dt.datetime.strftime(
            dt.datetime.now(dt.timezone.utc), "%Y-%m-%dT%H:%M:%SZ"
        ),
    )
