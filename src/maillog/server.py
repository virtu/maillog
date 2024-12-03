"""Maillog server functionality."""

import datetime as dt
import json
import logging as log
import os
import socket
import threading
import time
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import ClassVar

from maillog.cli.maillogd import Config
from maillog.message import Message, MessageBuffer
from maillog.requests import ClientRequestHandler


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
class MailLogServer(threading.Thread):
    """Mail log server."""

    conf: Config
    server_socket: socket.socket = field(init=False)
    buffer: MessageBuffer = MessageBuffer()
    request_handler: ClientRequestHandler = ClientRequestHandler(buffer)
    SOCKET: ClassVar[str] = "/run/maillog/server_socket"

    def __post_init__(self):
        super().__init__(name=self.__class__.__name__)

    def run(self):
        """Run the mail log server."""
        log.info("Started %s thread.", self.__class__.__name__)
        self.start_summary_mail_scheduler_thread()
        self.start_api_server_thread()

        self.setup_socket()

        while True:
            target = NextMailTarget.get(self.conf.schedule)
            log.info(
                "Sleeping for %s until %s", target.delta_string, target.time_string
            )
            time.sleep(target.delta_seconds)
            now = dt.datetime.now(dt.timezone.utc)
            log.info("Woke up at %s", now.strftime("%Y-%m-%dT%H:%M:%SZ"))

    def setup_socket(self):
        """Set up the server socket."""
        socket_path = Path(self.SOCKET)
        if socket_path.exists():
            log.debug("Removed existing socket (%s)", self.SOCKET)
            socket_path.unlink()
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.SOCKET)
        os.chmod(self.SOCKET, 0o666)
        log.debug("Created socket (%s)", self.SOCKET)

    def serve_forever(self):
        try:
            while True:
                client_socket, _ = self.server_socket.accept()
                threading.Thread(
                    target=self.handle_client, args=(client_socket,)
                ).start()
        finally:
            self.server_socket.close()
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)


if __name__ == "__main__":
    daemon = MailLogDaemon()
    daemon.serve_forever()
