"""Maillog command-line tool."""

import argparse
import datetime as dt
import json
import logging as log
import os
import socket
import sys
from dataclasses import asdict

from maillog.api import APISocket
from maillog.message import Message

# from .config import get_config

# maillog/cli.py


def main():
    """Main function for maillog CLI tool."""
    parser = argparse.ArgumentParser(description="Maillog CLI tool")
    subparsers = parser.add_subparsers(dest="command")

    send_parser = subparsers.add_parser("send", help="Send a message")
    send_parser.add_argument("message", help="Message to send")
    send_parser.add_argument(
        "--immediate", action="store_true", help="Send email immediately"
    )
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

    api_socket = APISocket.connect()
    if args.command == "send":
        message = Message(
            message=args.message,
            log_level=args.log_level,
            immediate=args.immediate,
        )
        api_socket.send(asdict(message))
        reply = api_socket.receive()
        print(json.dumps(reply, indent=2))
    elif args.command == "status":
        data = {"action": "status"}
        api_socket.send(data)
        status = api_socket.receive()
        print(json.dumps(status, indent=2))
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
