"""Import main function from maillogd."""

from .config import Config, EmailConfig
from .maillogd import main

__all__ = ["main", "Config", "EmailConfig"]
