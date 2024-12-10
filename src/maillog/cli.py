"""Maillog command-line tool."""

import argparse
import logging as log

import maillog
from maillog.api.client import get_status


def main():
    """Main function for maillog CLI tool."""
    parser = argparse.ArgumentParser(description="Maillog CLI tool")

    subparsers = parser.add_subparsers(dest="command")
    send_parser = subparsers.add_parser("event", help="Send a log event")
    send_parser.add_argument("message", help="Event text")
    send_parser.add_argument("--log-level", default="warning", help="Log level")

    _ = subparsers.add_parser("status", help="Get buffered messages")

    args = parser.parse_args()

    log.basicConfig(
        level="INFO",
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    if args.command == "event":
        if args.log_level.lower() == "warning":
            maillog.warning(args.message)
        elif args.log_level.lower() == "error":
            maillog.error(args.message)
        else:
            log.error("Invalid log level: %s", args.log_level)
    elif args.command == "status":
        get_status()
    else:
        parser.print_help()
