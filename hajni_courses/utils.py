import os
import yaml
from pathlib import Path
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, To, Subject, HtmlContent, Mail, SendGridException

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
    The HajniCoursesEmail objects are emails used by the project, and they have a public send method.
    To be used instead of the default Django solution.
    """

    def __init__(self, to, subject, message):
        self.email_config = load_config().get('hajni_courses_email', {})
        self.sg = None
        from_email = Email(os.environ.get('EMAIL_SENDER', self.email_config.get('sender')))
        to_email = To(to)
        subject = Subject(subject)
        content = HtmlContent(message)
        self.mail = Mail(from_email, to_email, subject, content)

    def __create_api_client(self):
        """
        Creates the Sendgrid API client using the API key.
        """
        self.sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY',
                                                           self.email_config.get('sendgrid_api_key')))

    def send(self):
        """
        Sends the email.
        """
        # workaround to make it work
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        try:
            if not settings.TEST_MODE:
                self.__create_api_client()
                response = self.sg.send(self.mail)
                return response
            return None
        except SendGridException:
            logger.error('The email with subject "{}" could not be sent to "{}"'.format(self.mail.subject, self.mail.to))
            return None
