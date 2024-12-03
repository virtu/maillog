"""Maillog command-line tool."""

import argparse
import json
import logging as log
import os
import socket
import sys

from maillog.api_server import APIServer

from .config import get_config

# maillog/cli.py


def send(msg, immediate=False, log_level="warning"):
    """Send message to API server."""
    data = {
        "action": "send",
        "msg": msg,
        "immediate": immediate,
        "log_level": log_level,
        "process_name": os.path.basename(sys.argv[0]),
        "process_id": os.getpid(),
    }
    _send_request(data)


def get_status():
    """Get status of API server."""
    data = {"action": "status"}
    return _send_request(data)


def _send_request(data):
    client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client_socket.connect(APIServer.SOCKET_PATH)
        client_socket.sendall(json.dumps(data).encode("utf-8"))
        response = ""
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            response += chunk.decode("utf-8")
        return json.loads(response)
    except FileNotFoundError as e:
        raise ConnectionError(
            f"Cannot connect to maillog daemon at {APIServer.SOCKET_PATH}"
        ) from e
    finally:
        client_socket.close()


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

    if args.command == "send":
        send(args.message, immediate=args.immediate, log_level=args.log_level)
        print("Message sent.")
    elif args.command == "status":
        status = get_status()
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
