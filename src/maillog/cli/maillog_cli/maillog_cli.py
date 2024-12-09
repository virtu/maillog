"""Maillog command-line tool."""

import argparse
import logging as log

import maillog
from maillog.api.client import get_status

# from .config import get_config

# maillog/cli.py


def main():
    """Main function for maillog CLI tool."""
    parser = argparse.ArgumentParser(description="Maillog CLI tool")
    subparsers = parser.add_subparsers(dest="command")

    send_parser = subparsers.add_parser("send", help="Send a message")
    send_parser.add_argument("message", help="Message to send")
    send_parser.add_argument("--log-level", default="warning", help="Log level")

    status_parser = subparsers.add_parser("status", help="Get buffered messages")

    args = parser.parse_args()

    log_level = "DEBUG"

    log.basicConfig(
        # level=conf.log_level,
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    if args.command == "send":
        if args.log_level == "warning":
            maillog.warning(args.message)
        # elif args.log_level == "error":
        #     error(args.message)
        else:
            log.error("Invalid log level: %s", args.log_level)
    elif args.command == "status":
        get_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


# def main():
#     """Parse command-line arguments, set up logging, and run maillog daemon."""
#
#     conf = get_config()
#     log.basicConfig(
#         level=conf.log_level,
#         format="%(asctime)s | %(levelname)-8s | %(message)s",
#         datefmt="%Y-%m-%dT%H:%M:%SZ",
#     )
#     log.Formatter.converter = time.gmtime
#     log.info("Using configuration: %s", conf)
#
#     buffer = MessageBuffer()
#     api_server = APIServer(buffer)
#     mail_scheduler = MailScheduler(conf.schedule, buffer)
#     # TODO: add log statements to run functions
#     api_server.start()
#     mail_scheduler.start()


if __name__ == "__main__":
    main()
