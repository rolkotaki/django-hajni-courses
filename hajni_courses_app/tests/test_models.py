from django.core.exceptions import ValidationError as django_ValidationError
from django.test import TestCase, Client
from django.urls import reverse
from django.db.utils import Error
from django.db import models
from unittest.mock import Mock, patch
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from hajni_courses_app.models import CustomUser, Course
from hajni_courses_app.utils.AccountActivationTokenGenerator import account_activation_token
from hajni_courses.utils import HajniCoursesEmail


class ModelsTestCase(TestCase):
    """
    Test cases for models.
    """

    def test_01_customuser_cancel(self):
        """Tests that we return False when the user cancellation fails during the save method."""
        with patch.object(CustomUser, 'save', return_value=None):
            with patch.object(HajniCoursesEmail, '__init__', return_value=None) as email_mock:
                email_mock.send = Mock()
                cu = CustomUser()
                cu.pk = 1
                cu.username = 'username'
                return_value = cu.cancel_user()
        self.assertTrue(return_value)

    def test_02_customuser_cancel_fails_with_save(self):
        """Tests that we return False when the user cancellation fails during the save method."""
        with patch.object(CustomUser, '__init__', return_value=None):
            with patch.object(CustomUser, 'save', side_effect=Error):
                cu = CustomUser()
                cu.pk = 1
                cu.username = 'username'
                return_value = cu.cancel_user()
        self.assertFalse(return_value)


class ActivateAccountTestCase(TestCase):
    """
    Test cases for the user account activation.
    """

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='user', password='test_password')

    def test_01_activate_user_account_successful(self):
        """Tests the successful activation of a user account."""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        response = self.client.post(reverse('activate_account', args=(uid, token)), follow=True)
        self.assertContains(response, '<div class="form_success_message">')
        self.assertContains(response, 'A fiókodat sikeresen aktiváltuk, most már be tudsz jelentkezni.')

    def test_02_activate_user_account_not_successful(self):
        """Tests when activating the user account fails because of an invalid uid."""
        uid = 'aaa'
        token = account_activation_token.make_token(self.user)
        response = self.client.post(reverse('activate_account', args=(uid, token)), follow=True)
        self.assertContains(response, '<div class="login_signup_errors">')
        self.assertContains(response, 'Az aktivációs link nem érvényes vagy hiba történt a fiókod aktiválása során.')

    def test_03_activate_user_account_not_successful(self):
        """Tests when activating the user account fails because of an invalid token."""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = 'aaa'
        response = self.client.post(reverse('activate_account', args=(uid, token)), follow=True)
        self.assertContains(response, '<div class="login_signup_errors">')
        self.assertContains(response, 'Az aktivációs link nem érvényes vagy hiba történt a fiókod aktiválása során.')

    def test_04_activate_user_account_not_successful(self):
        """Tests when activating the user account fails because a different user's pk was used in the decoding."""
        uid = urlsafe_base64_encode(force_bytes(CustomUser.objects.create_user(username='another_user',
                                                                               password='test_password').pk))
        token = account_activation_token.make_token(self.user)
        response = self.client.post(reverse('activate_account', args=(uid, token)), follow=True)
        self.assertContains(response, '<div class="login_signup_errors">')
        self.assertContains(response, 'Az aktivációs link nem érvényes vagy hiba történt a fiókod aktiválása során.')
