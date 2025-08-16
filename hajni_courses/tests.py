import unittest
from unittest.mock import mock_open, patch, Mock, MagicMock
from django.test import TestCase
from mailersend.exceptions import MailerSendError

from . import settings
from .utils import load_config, HajniCoursesEmail


class ProjectUtilsTestCase(unittest.TestCase):
    """
    Test cases for the project utils library.
    """

    @patch('builtins.open', mock_open(read_data='key: value'))
    def test_01_load_config_with_config_file(self):
        """Tests loading the config file when it exists."""
        config = load_config()
        self.assertDictEqual(config, {'key': 'value'})

    def test_02_load_config_without_config_file(self):
        """Tests loading the config file when it does not exist."""
        mo = mock_open()
        with patch('builtins.open', mo) as mocked_open:
            mocked_open.side_effect = FileNotFoundError
            config = load_config()
        self.assertDictEqual(config, {})

    @patch('builtins.open', mock_open())
    def test_03_load_config_without_config_file_when_none(self):
        """Tests loading the config file when it does not exist."""
        config = load_config()
        self.assertDictEqual(config, {})


class HajniCoursesEmailTestCase(TestCase):
    """
    Test cases for the HajniCoursesEmail class.
    """

    def test_01_email_when_not_testing(self):
        """Tests email sending when not in test mode."""
        with self.settings(TEST_MODE=False):
            HajniCoursesEmail._msc = Mock()
            HajniCoursesEmail._msc.emails.send = Mock(return_value="response")
            mail = HajniCoursesEmail(
                to="test@mail.com", subject="Test Subject", message="Test Message"
            )
            response = mail.send()
            self.assertEqual(response, "response")

    def test_02_email_when_testing(self):
        """Tests email sending when in test mode."""
        with self.settings(TEST_MODE=True):
            HajniCoursesEmail._msc = Mock()
            HajniCoursesEmail._msc.emails.send = Mock(return_value="response")
            mail = HajniCoursesEmail(
                to="test@mail.com", subject="Test Subject", message="Test Message"
            )
            ret = mail.send()
            self.assertIsNone(ret)
            HajniCoursesEmail._msc.send.assert_not_called()

    def test_03_email_when_mailersend_exception(self):
        """Tests email sending when there is a MailerSend error."""
        with self.settings(TEST_MODE=False):
            HajniCoursesEmail._msc = Mock()
            HajniCoursesEmail._msc.emails.send = Mock(side_effect=MailerSendError("Test error"))
            mail = HajniCoursesEmail(
                to="test@mail.com", subject="Test Subject", message="Test Message"
            )
            response = mail.send()
            self.assertIsNone(response)

    def test_04_email_when_exception(self):
        """Tests email sending when there is an error."""
        with self.settings(TEST_MODE=False):
            HajniCoursesEmail._msc = Mock()
            HajniCoursesEmail._msc.emails.send = Mock(side_effect=Exception())
            mail = HajniCoursesEmail(
                to="test@mail.com", subject="Test Subject", message="Test Message"
            )
            response = mail.send()
            self.assertIsNone(response)

    def test_05_get_client(self):
        """Test that _get_client() creates a new client when none exists."""
        HajniCoursesEmail._msc = None
        self.assertIsNone(HajniCoursesEmail._msc)

        with patch("hajni_courses.utils.MailerSendClient") as mock_mailersend_client:
            mock_instance = MagicMock()
            mock_mailersend_client.return_value = mock_instance

            # First call should create the client
            client = HajniCoursesEmail._get_client()
            # Second call should return the same client without creating a new one
            client_2 = HajniCoursesEmail._get_client()

            # Verify the client was created only once with correct API key
            mock_mailersend_client.assert_called_once_with(
                api_key=settings.MAILERSEND_API_KEY
            )
            self.assertTrue(client == client_2 == mock_instance)
            self.assertEqual(HajniCoursesEmail._msc, mock_instance)
