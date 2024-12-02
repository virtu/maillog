"""Maillog daemon."""

import logging as log
import time

from maillog.server import MailLogServer

from .config import get_config


def main():
    """Parse command-line arguments, set up logging, and run darkseed daemon."""

    conf = get_config()
    log.basicConfig(
        level=conf.log_level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    log.Formatter.converter = time.gmtime
    log.info("Using configuration: %s", conf)

    maillog_server = MailLogServer(conf)
    maillog_server.start()


if __name__ == "__main__":
    main()
