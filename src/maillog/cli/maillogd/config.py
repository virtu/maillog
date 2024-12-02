"""Configuration options for maillog daemon."""

import argparse
import datetime
import importlib.metadata
import os
from dataclasses import asdict, dataclass
from pathlib import Path

__version__ = importlib.metadata.version("maillog")


@dataclass(frozen=True)
class EmailConfig:
    """Email configuration."""

    to: str  # recipient address
    sender: str  # sender address
    server: str  # smtp server hostname
    port: str  # smtp server port
    username: str  # smtp server username
    password: str  # smtp server password

    @staticmethod
    def read_password(password_file: str) -> str:
        """Read password from file."""
        file = Path(password_file)
        if not file.exists():
            raise FileNotFoundError(f"Password file '{password_file}' not found")
        if not file.is_file():
            raise ValueError(f"Password file '{password_file}' is not a file")
        password = file.read_text(encoding="UTF-8").strip()
        return password

    @classmethod
    def parse(cls, args):
        """Create class instance from arguments."""

        password = EmailConfig.read_password(args.password_file)
        return cls(
            to=args.to,
            sender=args.sender,
            server=args.server,
            port=args.port,
            username=args.username,
            password=password,
        )

    def __repr__(self):
        """
        Custom repr method to hide password from logs.

        Used by print() and str() when there is no dedicated __str__ method.
        """

        return (
            f"EmailConfig(to={self.to}, sender={self.sender}, server={self.server}, "
            f"port={self.port}, username={self.username}, password=********)"
        )


@dataclass(frozen=True)
class Config:
    """Configuration settings for the daemon."""

    version: str
    timestamp: datetime.datetime
    log_level: str
    email: EmailConfig
    schedule: datetime.time

    @classmethod
    def parse(cls, args):
        """Create class instance from arguments."""

        return cls(
            version=__version__,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            log_level=args.log_level.upper(),
            email=EmailConfig.parse(args),
            schedule=datetime.datetime.strptime(args.schedule, "%H:%M").time(),
        )

    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


def parse_args():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--log-level",
        type=str,
        default=os.environ.get("LOG_LEVEL", "INFO"),
        help="Logging verbosity",
    )

    parser.add_argument(
        "--schedule",
        type=str,
        default="23:59",
        help="UTC time when to send summary mail of all messages buffered that day (format: HH:MM, default: 23:59)",
    )

    parser.add_argument(
        "--to", type=str, required=True, help="Recipient address for emails."
    )

    parser.add_argument(
        "--sender", type=str, required=True, help="Sender address for emails."
    )

    parser.add_argument(
        "--server",
        type=str,
        required=True,
        help="SMTP server address for sending emails.",
    )

    parser.add_argument(
        "--port",
        type=int,
        required=True,
        help="SMTP server port for sending emails.",
    )

    parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="SMTP account username for sending emails.",
    )

    parser.add_argument(
        "--password-file",
        type=str,
        required=True,
        help="File containing SMTP account password for sending emails.",
    )

    args = parser.parse_args()

    return args


def get_config():
    """Parse command-line arguments and get configuration settings."""

    args = parse_args()
    conf = Config.parse(args)
    return conf
