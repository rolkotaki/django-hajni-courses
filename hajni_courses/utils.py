import os
import yaml
from pathlib import Path
from django.conf import settings
from django.db.models.query import QuerySet
from mailersend import MailerSendClient, EmailBuilder
from mailersend.exceptions import MailerSendError
from mailersend.resources.email import EmailRequest, APIResponse
from threading import RLock

from .logger import logger


CONFIG_FILE = os.path.join(Path(__file__).resolve().parent.parent, 'config.yml')


def load_config():
    """
    Returns the content of the config file.
    """
    try:
        with open(CONFIG_FILE) as config_file:
            config = yaml.safe_load(config_file)
            if not config:
                return {}
    except FileNotFoundError:
        return {}
    return config


class HajniCoursesEmail:
    """
    Represents an email to be sent via MailerSend.
    To be used instead of the default Django solution.
    """
    _msc: MailerSendClient = None
    _msc_lock: RLock = RLock()
    email_config: dict = load_config().get('hajni_courses_email', {})

    def __init__(self, to: str | QuerySet, subject: str, message: str):
        self.to: str | QuerySet = to
        self.subject: str = subject
        self.message: str = message
        email_builder = (
            EmailBuilder()
            .from_email(os.environ.get('EMAIL_SENDER', self.email_config.get('sender')),
                        settings.EMAIL_FROM_NAME)
            .subject(self.subject)
            .html(self.message)
        )
        if type(to) is QuerySet:
            for recipient in to:
                email_builder.to(str(recipient))
        else:
            email_builder.to(str(to))
        self.email: EmailRequest = email_builder.build()

    @classmethod
    def _get_client(cls) -> MailerSendClient:
        """Get or create the MailerSend client."""
        if cls._msc is None:
            with cls._msc_lock:
                if cls._msc is None:
                    cls._msc = MailerSendClient(api_key=os.environ.get('MAILERSEND_API_KEY',
                                                                       cls.email_config.get('mailersend_api_key')))
        return cls._msc

    def send(self) -> APIResponse | None:
        """
        Send the email.
        """
        try:
            if settings.TEST_MODE:
                return None
            response = self._get_client().emails.send(self.email)
            return response
        except MailerSendError as se:
            logger.error(
                f"Failed to send email to {self.to} with subject {self.subject} due to MailerSendError: {str(se)}",
                exc_info=True,
            )
            return None
        except Exception as e:
            logger.error(
                f"Failed to send email to {self.to} with subject {self.subject}: {str(e)}",
                exc_info=True,
            )
            return None
