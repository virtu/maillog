"""Maillog server functionality."""

import logging as log
import threading
import time
from dataclasses import dataclass

from maillog.cli.maillogd import Config


@dataclass(unsafe_hash=True)
class MailLogServer(threading.Thread):
    """Mail log server."""

    conf: Config

    def __post_init__(self):
        super().__init__(name=self.__class__.__name__)

    def run(self):
        log.info("Started %s thread.", self.__class__.__name__)

        refresh = 10
        while True:
            log.debug("Sleeping for %d seconds", refresh)
            time.sleep(refresh)
            log.debug("Waking after %d seconds", refresh)
