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

from maillog.cli.maillogd import Config
from maillog.message import Message, MessageBuffer


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
    SOCKET: ClassVar[str] = "/run/maillog/server_socket"

    def __post_init__(self):
        super().__init__(name=self.__class__.__name__)

    def run(self):
        log.info("Started %s thread.", self.__class__.__name__)
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

    def send_summary_email(self):
        content = ""
        for process_key, messages in self.message_buffer.items():
            content += f"Process: {process_key}\n"
            for msg in messages:
                timestamp = msg["timestamp"]
                log_level = msg["log_level"]
                message = msg["msg"]
                content += f"[{timestamp}] [{log_level}] {message}\n"
            content += "\n"
        subject = f"maillog: daily log from {self.hostname} for {datetime.date.today().isoformat()}"
        self.send_email(subject, content)

    def send_email(self, subject, content):
        msg = MIMEText(content)
        msg["Subject"] = subject
        msg["From"] = self.email_credentials["from_address"]
        msg["To"] = self.email_credentials["to_address"]

        try:
            with smtplib.SMTP(
                self.email_credentials["smtp_server"],
                self.email_credentials["smtp_port"],
            ) as server:
                server.starttls()
                server.login(
                    self.email_credentials["username"],
                    self.email_credentials["password"],
                )
                server.send_message(msg)
        except Exception as e:
            logging.error(f"Failed to send email: {e}")

    def handle_client_request(self, client_socket):
        """Handle incoming client requests."""
        try:
            data = ""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk.decode("utf-8")
            if data:
                request = json.loads(data)
                action = request.get("action")
                if action == "send":
                    self.handle_send(request, client_socket)
                elif action == "status":
                    self.handle_status(client_socket)
                else:
                    log.warning("Unknown action: %s", action)
        finally:
            client_socket.close()

    def handle_send(self, request, client_socket):
        """Handle send request from client."""

        timestamp = dt.datetime.now(dt.timezone.utc)
        msg = request.get("msg")
        immediate = request.get("immediate", False)
        log_level = request.get("log_level", "warning")
        process_name = request.get("process_name", "unknown")
        process_id = request.get("process_id", "unknown")

        log_func = getattr(log, log_level, log.warning)
        log_func(f"[{process_name}][{process_id}] {msg} (logging from maillog)")

        message = Message(
            timestamp=timestamp,
            process_name=process_name,
            process_id=process_id,
            message=msg,
            log_level=log_level,
        )

        if immediate:
            raise NotImplementedError("Immediate sending not implemented yet.")
            # subject = f"maillog: urgent message from {process_name} on {self.hostname}"
            # content = f"[{timestamp}] [{log_level}] {msg}\nProcess: {process_name}\nPID: {process_id}"
            # self.send_email(subject, content)
        else:
            self.buffer.insert(message)

        client_socket.sendall(json.dumps({"status": "ok"}).encode("utf-8"))

    def handle_status(self, client_socket):
        with self.buffer_lock:
            response = {"buffer": self.message_buffer}
        client_socket.sendall(json.dumps(response).encode("utf-8"))

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
