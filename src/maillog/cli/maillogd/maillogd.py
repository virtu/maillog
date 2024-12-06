"""Maillog daemon."""

import logging as log
import time

from maillog.api import APIServer
from maillog.event import EventBuffer
from maillog.scheduler import MailScheduler

from .config import get_config


def main():
    """Parse command-line arguments, set up logging, and run maillog daemon."""

    conf = get_config()
    log.basicConfig(
        level=conf.log_level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    log.Formatter.converter = time.gmtime
    log.info("Using configuration: %s", conf)

    buffer = EventBuffer()
    api_server = APIServer(buffer)
    mail_scheduler = MailScheduler(conf.schedule, buffer)
    api_server.start()
    mail_scheduler.start()


if __name__ == "__main__":
    main()
