"""Module containing functionality to schedule daily summary emails."""

import datetime as dt
import logging as log
import threading
import time
from dataclasses import dataclass
from functools import cached_property

from maillog.message import MessageBuffer


@dataclass
class NextMailTarget:
    """Next scheduled target for sending the summary mail."""

    time: dt.datetime
    delta: dt.timedelta

    @cached_property
    def time_string(self):
        """Return target time in human readable format."""
        return self.time.strftime("%Y-%m-%dT%H:%MZ")

    @cached_property
    def delta_seconds(self):
        """Get the time in seconds until next scheduled run."""
        return self.delta.total_seconds()

    @cached_property
    def delta_string(self):
        """Get the time in human readable format (hours, minutes, seconds) until next scheduled run."""
        return (
            f"{self.delta.seconds // 3600}h "
            f"{(self.delta.seconds // 60) % 60}m "
            f"{self.delta.seconds % 60}s"
        )

    @classmethod
    def get(cls, schedule: dt.time) -> "NextMailTarget":
        """Get the next scheduled target."""
        now = dt.datetime.now(dt.timezone.utc)
        target = dt.datetime.combine(now.date(), schedule, tzinfo=dt.timezone.utc)
        # If past today's target time, schedule for same time tomorrow
        if now >= target:
            target += dt.timedelta(days=1)
        delta = target - now
        return cls(target, delta)


@dataclass(unsafe_hash=True)
class MailScheduler(threading.Thread):
    """Scheduler for sending daily summary emails."""

    # mailer: Mailer
    # conf: Config
    schedule: dt.time
    buffer: MessageBuffer

    def __post_init__(self):
        # TODO: TEST IF THIS IS REALLY NECESSARY
        """Initialize the parent class."""
        super().__init__(name=self.__class__.__name__)

    def run(self):
        """
        Start the scheduler.

        This function is called by the Threading class's start method.
        """
        log.info("Started %s thread.", self.__class__.__name__)

        while True:
            target = NextMailTarget.get(self.schedule)
            log.info(
                "Sleeping for %s until %s", target.delta_string, target.time_string
            )
            time.sleep(target.delta_seconds)
            now = dt.datetime.now(dt.timezone.utc)
            log.info("Woke up at %s", now.strftime("%Y-%m-%dT%H:%M:%SZ"))
            log.info("This is where I would send the summary email.")
            # make sure to use lock? shouldn't have to. all locking should go into buffer
