"""Maillog server functionality."""

from dataclasses import dataclass, field

from maillog.api_server import APIServer
from maillog.cli.maillogd import Config
from maillog.message import MessageBuffer
from maillog.scheduler import MailScheduler


@dataclass
class Server:
    """
    Maillog server that wraps components together:

    APIServer: to handle incoming requests
    Buffer: to buffer incoming messages
    MailScheduler: to send daily summary emails
    Mailer: to send emails
    """

    api_server: APIServer = field(init=False)
    mail_scheduler: MailScheduler = field(init=False)

    def start(self, conf: Config):
        """Entry point for starting the maillog server."""
        buffer = MessageBuffer()
        self.api_server = APIServer(buffer)
        self.mail_scheduler = MailScheduler(conf.schedule, buffer)
        # print("Server is starting both threads.")
        # TODO: add log statements to run functions
        self.api_server.start()
        self.mail_scheduler.start()

    def stop(self):
        """Stop the maillog server."""
        print("Server is stopping both threads.")
        self.api_server.join()
        self.mail_scheduler.join()
        print("Server has stopped both threads.")
