import math
import copy
import re
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

from hajni_courses_app.models import CustomUser, Course
from hajni_courses_app.utils.constants import COURSES_PER_PAGE, PAGINATION_PAGES


class BaseViewTestCase(TestCase):
    """
    Test cases for the base view.
    """

    def _login(self, admin=False):
        """Logs in a superuser or a normal user."""
        self.client = Client()
        if admin:
            self.user = CustomUser.objects.create_superuser(username='admin', password='admin_password')
        else:
            self.user = CustomUser.objects.create_user(username='user', password='test_password')
        self.client.force_login(user=self.user)

    def test_01_signup_displayed_when_not_logged_in(self):
        """Tests that the signup option is displayed when user is not logged in."""
        response = self.client.get(reverse('home'))
        html_content = response.content.decode('utf-8')
        pattern = r'<a id="nav_signup" class="menu_item_right" href="(.*)">Regisztráció</a>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)

    def test_02_login_displayed_when_not_logged_in(self):
        """Tests that the login option is displayed when user is not logged in."""
        response = self.client.get(reverse('home'))
        html_content = response.content.decode('utf-8')
        pattern = r'<a id="nav_login" class="menu_item_right" href="(.*)">Bejelentkezés</a>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)

    def test_03_profile_not_displayed_when_not_logged_in(self):
        """Tests that the user profile option is not displayed when user is not logged in."""
        response = self.client.get(reverse('home'))
        html_content = response.content.decode('utf-8')
        pattern = r'<button class="dropdown_button">Profilom</button>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNone(match)

    def test_04_signup_not_displayed_when_logged_in(self):
        """Tests that the signup option is not displayed when user is logged in."""
        self._login()
        response = self.client.get(reverse('home'))
        html_content = response.content.decode('utf-8')
        pattern = r'<a class="menu_item_right" href="(.*)">Regisztráció</a>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNone(match)

    def test_05_login_not_displayed_when_logged_in(self):
        """Tests that the login option is not displayed when user is logged in."""
        self._login()
        response = self.client.get(reverse('home'))
        html_content = response.content.decode('utf-8')
        pattern = r'<a class="menu_item_right" href="(.*)">Bejelentkezés</a>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNone(match)

    def test_06_profile_displayed_when_logged_in(self):
        """Tests that the user profile option is displayed when user is logged in."""
        self._login()
        response = self.client.get(reverse('home'))
        html_content = response.content.decode('utf-8')
        pattern = r'<button id="user_dropdown_button" class="dropdown_button">Profilom</button>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)

    def test_07_delete_profile_displayed_only_when_normal_user_logged_in(self):
        """Tests that the login option is displayed when user is not logged in."""
        # not logged
        response = self.client.get(reverse('home'))
        html_content = response.content.decode('utf-8')
        pattern = r'<a id="nav_delete_profile"(.*)</a>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNone(match)
        # logged in as normal user
        self._login()
        response = self.client.get(reverse('home'))
        html_content = response.content.decode('utf-8')
        pattern = r'<a id="nav_delete_profile"(.*)</a>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)
        # logged in as staff user
        self._login(admin=True)
        response = self.client.get(reverse('home'))
        html_content = response.content.decode('utf-8')
        pattern = r'<a id="nav_delete_profile"(.*)</a>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNone(match)


class HomeTestCase(TestCase):
    """
    Test cases for the Home view.
    """

    def _login(self):
        """Logs in a normal user."""
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='user', password='test_password',
                                                   phone_number='0036301234567')
        self.client.force_login(user=self.user)

    def test_01_home_rendering(self):
        """Tests that the home view is rendered successfully and the correct template is used."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'home.html')

    def test_02_call_me_is_disabled_when_not_logged_in(self):
        """Tests that the apply option is not available for users not logged in."""
        response = self.client.get(reverse('home'))
        self.assertContains(response, '<input name="call_me"')
        html_content = response.content.decode('utf-8')
        pattern = r'<input name="call_me" class="a_button green_button(.*)disabled_button(.*)"(.*)Hívj Vissza(.*)/>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)

    def test_03_call_me_is_enabled_when_logged_in(self):
        """Tests that the apply option is available for users logged in."""
        self._login()
        response = self.client.get(reverse('home'))
        self.assertContains(response, '<input name="call_me"')
        html_content = response.content.decode('utf-8')
        pattern = r'<input name="call_me" class="a_button green_button(.*)disabled_button(.*)"(.*)Hívj Vissza(.*)/>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNone(match)
        pattern = r'<input name="call_me" class="a_button green_button(.*)Hívj Vissza(.*)/>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)

    def test_04_send_callback_request(self):
        """Tests sending a callback request from the Home view."""
        self._login()
        response = self.client.post(reverse('home'), {'call_me': 'call_me'}, follow=True)
        self.assertContains(response, '<div class="form_success_message"')
        self.assertContains(response, 'Visszahívási kérelmedet elküldtük.')
        # to test that the message is only displayed when required
        response = self.client.post(reverse('home'), {'dont_call_me': 'dont_call_me'}, follow=True)
        self.assertNotContains(response, 'Visszahívási kérelmedet elküldtük.')

    def test_05_send_callback_without_phone_number(self):
        """Tests sending a callback request from the Home view."""
        # user without phone number
        user = CustomUser.objects.create_user(username='user', password='test_password')
        self.client.force_login(user=user)
        response = self.client.post(reverse('home'), {'call_me': 'call_me'}, follow=True)
        self.assertContains(response, 'Önnek nincs megadva telefonszám, így nem kérhet visszahívást.')


class LogInTestCase(TestCase):
    """
    Test cases for the LogIn view.
    """

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='user', password='test_password')

    def test_01_login_rendering(self):
        """Tests that the login view is rendered successfully and the correct template is used."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'login.html')

    def test_02_successful_login(self):
        """Tests a successful login."""
        response = self.client.post(reverse('login'), {'username': 'user', 'password': 'test_password'})
        self.assertRedirects(response, reverse('home'))

    def test_03_unsuccessful_login(self):
        """Tests an unsuccessful login."""
        response = self.client.post(reverse('login'), {'username': 'user', 'password': 'wrong'})
        self.assertContains(response, 'Helytelen felhasználónév vagy jelszó!')

    def test_04_empty_username_field(self):
        """Tests when the username field is empty."""
        response = self.client.post(reverse('login'), {'username': '', 'password': 'test_password'})
        self.assertContains(response, '<ul class="error_list">')

    def test_05_empty_password_field(self):
        """Tests when the password field is empty."""
        response = self.client.post(reverse('login'), {'username': 'user', 'password': ''})
        self.assertContains(response, '<ul class="error_list">')

    def test_06_inactive_user_login(self):
        """Tests when the user is inactive."""
        inactive_user = CustomUser.objects.create_user(username='inactive_user', password='test_password',
                                                       is_active=False)
        response = self.client.post(reverse('login'), {'username': 'inactive_user', 'password': 'test_password'})
        self.assertContains(response, 'Helytelen felhasználónév vagy jelszó!')


class SignUpTestCase(TestCase):
    """
    Test cases for the SignUp view.
    """

    def setUp(self):
        self.signup_attr = {
            'first_name': 'Firstname',
            'last_name': 'Lastname',
            'email': 'somebody@mail.com',
            'phone_number': '+36991234567',
            'username': 'test_user',
            'password1': 'AldPoE672@8',
            'password2': 'AldPoE672@8',
            'privacy_policy': 'accepted'
        }

    def test_01_signup_rendering(self):
        """Tests that the signup view is rendered successfully and the correct template is used."""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'signup.html')

    def test_02_successful_signup(self):
        """Tests a successful signup."""
        response = self.client.post(reverse('signup'), self.signup_attr)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, '<div class="form_success_message_top">')
        # self.assertContains(response, "A fiókodat sikeresen létrehoztuk, kérlek fejezd be a regisztrációt az "
        #                               "emailben küldött aktivációs linkre kattintással.")

    def test_03_empty_signup_fields(self):
        """Tests for each field when it is empty when trying to sign up."""
        for field in ['first_name', 'last_name', 'email', 'username', 'password1', 'password2', 'privacy_policy']:
            signup_attr_copy = copy.deepcopy(self.signup_attr)
            signup_attr_copy[field] = ''
            response = self.client.post(reverse('signup'), signup_attr_copy)
            self.assertContains(response, '<ul class="error_list">')


class PersonalDataTestCase(TestCase):
    """
    Test cases for the Personal Data view.
    """

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='user', password='test_password', email='somebody@mail.com')
        self.pers_data_attr = {
            'first_name': 'Firstname',
            'last_name': 'Lastname',
            'email': 'somebody@mail.com',
            'phone_number': '+36991234567'
        }

    def test_01_personal_data_not_displayed_when_not_logged_in(self):
        """Tests that personal is not displayed when user is not logged in."""
        response = self.client.get(reverse('personal_data'))
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('personal_data'))

    def test_02_personal_data_displayed_when_logged_in(self):
        """Tests that personal is displayed when user is logged in."""
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('personal_data'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'personal_data.html')

    def test_03_personal_data_empty_fields(self):
        """Tests for each field when it is empty when trying to update the personal data."""
        self.client.force_login(user=self.user)
        for field in ['first_name', 'last_name', 'email']:
            pers_data_attr_copy = copy.deepcopy(self.pers_data_attr)
            pers_data_attr_copy[field] = ''
            response = self.client.post(reverse('personal_data'), pers_data_attr_copy)
            self.assertContains(response, '<ul class="error_list">')

    def test_04_personal_data_successful_update_without_email(self):
        """Tests a successful update of the personal data without email change."""
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('personal_data'), self.pers_data_attr, follow=True)
        self.assertContains(response, '<div class="form_success_message">')
        self.assertContains(response, 'Az adataidat sikeresen frissítettük.')

    def test_05_personal_data_successful_update_with_email(self):
        """Tests a successful update of the personal data with email change included."""
        self.pers_data_attr['email'] = 'new@mail.com'
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('personal_data'), self.pers_data_attr, follow=True)
        self.assertContains(response, '<div class="form_success_message">')
        # self.assertContains(response, "Az adataidat sikeresen frissítettük és küldtünk egy emailt, hogy meg tudd "
        #                               "erősíteni az új email címedet.")


class DeleteProfileTestCase(TestCase):
    """
    Test cases for the Delete Profile view.
    """

    def _login(self):
        """Logs in a normal user."""
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='user', password='test_password',
                                                   phone_number='0036301234567')
        self.client.force_login(user=self.user)

    def test_01_delete_profile_not_displayed_when_not_logged_in(self):
        """Tests that delete profile view is not displayed when user is not logged in."""
        response = self.client.get(reverse('delete_profile'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('delete_profile'))

    def test_02_delete_profile_rendering(self):
        """Tests that the delete profile view is rendered successfully and the correct template is used."""
        self._login()
        response = self.client.get(reverse('delete_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'delete_profile.html')

    def test_03_delete_profile_error(self):
        """Tests when an error happens during deleting the user profile."""
        self._login()
        with patch.object(CustomUser, 'delete_user_profile', return_value=False):
            response = self.client.post(reverse('delete_profile'), {'delete_profile': 'delete_profile'}, follow=True)
        self.assertContains(response, 'Hiba történt profilod törlése közben. Lépj kapcsolatba velünk.')

    def test_04_delete_profile(self):
        """Tests deleting the user profile."""
        self._login()
        response = self.client.post(reverse('delete_profile'), {'delete_profile': 'delete_profile'}, follow=False)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(CustomUser.objects.count(), 0)


class CourseViewTestCase(TestCase):
    """
    Test cases for the General/Pensioner Courses and Course views.
    """

    def _create_course(self, course_number=''):
        course_attrs = {
            'name': 'course_name{}'.format(course_number),
            'price': 10000,
            'description': '*one*two*three',
            'duration': '3 times 90 minutes',
            'for_pensioners': True,
            'for_non_pensioners': True,
            'active': True
        }
        return Course.objects.create(**course_attrs)

    def setUp(self):
        self.course = self._create_course()

    def _login(self):
        """Logs in a normal user."""
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='user', password='test_password')
        self.client.force_login(user=self.user)

    def test_01_general_course_list_rendering(self):
        """Tests that the general courses view is rendered successfully and the correct template is used."""
        response = self.client.get(reverse('general_courses'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'general_courses.html')

    def test_02_pensioner_course_list_rendering(self):
        """Tests that the general courses view is rendered successfully and the correct template is used."""
        response = self.client.get(reverse('pensioner_courses'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'pensioner_courses.html')

    def test_03_general_course_box_is_displayed(self):
        """Tests that the general course box is displayed indeed in the General Courses view."""
        # this SHOULD be displayed on the general courses page
        course_attrs = {
            'name': 'general_course_name',
            'price': 10000,
            'description': '*one*two*three',
            'duration': '3 times 90 minutes',
            'for_pensioners': False,
            'for_non_pensioners': True,
            'active': True
        }
        Course.objects.create(**course_attrs)
        # this should NOT be displayed on the general courses page
        course_attrs = {
            'name': 'pensioner_course_name',
            'price': 10000,
            'description': '*one*two*three',
            'duration': '3 times 90 minutes',
            'for_pensioners': True,
            'for_non_pensioners': False,
            'active': True
        }
        Course.objects.create(**course_attrs)

        response = self.client.get(reverse('general_courses'))
        self.assertContains(response, '<div class="course_box">')
        html_content = response.content.decode('utf-8')
        # both general and pensioner
        pattern = r'<p class="course_box_name">(.*)course_name(.*)</p>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)
        # only general
        pattern = r'<p class="course_box_name">(.*)general_course_name(.*)</p>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)
        # only pensioner
        pattern = r'<p class="course_box_name">(.*)pensioner_course_name(.*)</p>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNone(match)

    def test_04_pensioner_course_box_is_displayed(self):
        """Tests that the general course box is displayed indeed in the General Courses view."""
        # this should NOT be displayed on the general courses page
        course_attrs = {
            'name': 'general_course_name',
            'price': 10000,
            'description': '*one*two*three',
            'duration': '3 times 90 minutes',
            'for_pensioners': False,
            'for_non_pensioners': True,
            'active': True
        }
        Course.objects.create(**course_attrs)
        # this SHOULD  be displayed on the general courses page
        course_attrs = {
            'name': 'pensioner_course_name',
            'price': 10000,
            'description': '*one*two*three',
            'duration': '3 times 90 minutes',
            'for_pensioners': True,
            'for_non_pensioners': False,
            'active': True
        }
        Course.objects.create(**course_attrs)

        response = self.client.get(reverse('pensioner_courses'))
        self.assertContains(response, '<div class="course_box">')
        html_content = response.content.decode('utf-8')
        # both general and pensioner
        pattern = r'<p class="course_box_name">(.*)course_name(.*)</p>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)
        # only general
        pattern = r'<p class="course_box_name">(.*)general_course_name(.*)</p>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNone(match)
        # only pensioner
        pattern = r'<p class="course_box_name">(.*)pensioner_course_name(.*)</p>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)

    def test_05_course_rendering(self):
        """Tests that the course view is rendered successfully and the correct template is used."""
        response = self.client.get(reverse('course', args=(self.course.slug,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'course.html')

    def test_06_course_is_displayed(self):
        """Tests that the course is indeed displayed successfully in the Course view."""
        response = self.client.get(reverse('course', args=(self.course.slug,)))
        self.assertContains(response, '<div class="course">')
        html_content = response.content.decode('utf-8')
        pattern = r'<p class="course_name">(.*)course_name(.*)</p>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)

    def test_07_apply_is_disabled_when_not_logged_in(self):
        """Tests that the apply option is not available for users not logged in."""
        response = self.client.get(reverse('course', args=(self.course.slug,)))
        self.assertContains(response, '<div class="course">')
        html_content = response.content.decode('utf-8')
        pattern = r'<a class="a_button green_button(.*)disabled_button(.*)" href(.*)Jelentkezek(.*)</a>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)

    def test_08_apply_is_enabled_when_logged_in(self):
        """Tests that the apply option is available for users logged in."""
        self._login()
        response = self.client.get(reverse('course', args=(self.course.slug,)))
        self.assertContains(response, '<div class="course">')
        html_content = response.content.decode('utf-8')
        pattern = r'<a class="a_button green_button(.*)disabled_button(.*)" href(.*)Jelentkezek(.*)</a>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNone(match)
        pattern = r'<a class="a_button green_button( ?)" href(.*)Jelentkezek(.*)</a>'
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match)

    def test_09_pagination_not_displayed(self):
        """Tests that the pagination is not displayed when we have no more items than the maximum allowed on a page."""
        response = self.client.get(reverse('general_courses'))
        self.assertNotContains(response, '<div class="pagination">')
        response = self.client.get(reverse('pensioner_courses'))
        self.assertNotContains(response, '<div class="pagination">')

    def test_10_pagination_is_displayed(self):
        """Tests that the pagination is displayed when we have more items than the maximum allowed on a page."""
        for i in range(COURSES_PER_PAGE):
            self._create_course(str(i + 1))  # so that we have one more course than the maximum allowed on a page
        response = self.client.get(reverse('general_courses'))
        # general courses
        self.assertContains(response, '<div class="pagination">')
        self.assertContains(response, '<a class="page_link" href="?page=2">utolsó &raquo;</a>')
        self.assertNotContains(response, '<a class="page_link" href="?page=1">&laquo; első</a>')
        # pensioner courses
        response = self.client.get(reverse('pensioner_courses'))
        self.assertContains(response, '<div class="pagination">')
        self.assertContains(response, '<a class="page_link" href="?page=2">utolsó &raquo;</a>')
        self.assertNotContains(response, '<a class="page_link" href="?page=1">&laquo; első</a>')

    def test_11_general_pagination_links_are_correct(self):
        """Tests that the pagination links are all displayed correctly on the General Courses view."""
        for i in range(COURSES_PER_PAGE * PAGINATION_PAGES):
            self._create_course(str(i + 1))
        response = self.client.get(reverse('general_courses'), {'page': 2})
        self.assertContains(response, '<div class="pagination">')
        self.assertContains(response, '<a class="page_link" href="?page={}">utolsó &raquo;</a>'.format(
            PAGINATION_PAGES + 1))
        self.assertContains(response, '<a class="page_link" href="?page=1">&laquo; első</a>')
        self.assertContains(response, '<span class="current_page">2</span>')

        response = self.client.get(reverse('general_courses'), {'page': PAGINATION_PAGES})
        self.assertContains(response, '<div class="pagination">')
        self.assertContains(response, '<a class="page_link" href="?page={}">utolsó &raquo;</a>'.format(
            PAGINATION_PAGES + 1))
        self.assertContains(response, '<a class="page_link" href="?page=1">&laquo; első</a>')
        self.assertContains(response, '<span class="current_page">{}</span>'.format(PAGINATION_PAGES))

        response = self.client.get(reverse('general_courses'))
        self.assertContains(response, '<div class="pagination">')
        self.assertContains(response, '<a class="page_link" href="?page={}">utolsó &raquo;</a>'.format(
            PAGINATION_PAGES + 1))
        self.assertNotContains(response, '<a class="page_link" href="?page=1">&laquo; első</a>')

        response = self.client.get(reverse('general_courses'), {'page': PAGINATION_PAGES + 1})
        self.assertContains(response, '<div class="pagination">')
        self.assertNotContains(response, '<a class="page_link" href="?page={}">utolsó &raquo;</a>'.format(
            PAGINATION_PAGES + 1))
        self.assertContains(response, '<a class="page_link" href="?page=1">&laquo; első</a>')

        for i in range(COURSES_PER_PAGE):
            self._create_course(str((COURSES_PER_PAGE * PAGINATION_PAGES + 1) + i + 1))
        response = self.client.get(reverse('general_courses'), {'page': math.ceil(PAGINATION_PAGES / 2)})
        self.assertContains(response, '<div class="pagination">')
        self.assertContains(response, '<a class="page_link" href="?page={}">utolsó &raquo;</a>'.format(
            PAGINATION_PAGES + 2))
        self.assertContains(response, '<a class="page_link" href="?page=1">&laquo; első</a>')

    def test_12_pensioner_pagination_links_are_correct(self):
        """Tests that the pagination links are all displayed correctly on the Pensioner Courses view."""
        for i in range(COURSES_PER_PAGE * PAGINATION_PAGES):
            self._create_course(str(i + 1))
        response = self.client.get(reverse('pensioner_courses'), {'page': 2})
        self.assertContains(response, '<div class="pagination">')
        self.assertContains(response, '<a class="page_link" href="?page={}">utolsó &raquo;</a>'.format(
            PAGINATION_PAGES + 1))
        self.assertContains(response, '<a class="page_link" href="?page=1">&laquo; első</a>')
        self.assertContains(response, '<span class="current_page">2</span>')

        response = self.client.get(reverse('pensioner_courses'), {'page': PAGINATION_PAGES})
        self.assertContains(response, '<div class="pagination">')
        self.assertContains(response, '<a class="page_link" href="?page={}">utolsó &raquo;</a>'.format(
            PAGINATION_PAGES + 1))
        self.assertContains(response, '<a class="page_link" href="?page=1">&laquo; első</a>')
        self.assertContains(response, '<span class="current_page">{}</span>'.format(PAGINATION_PAGES))

        response = self.client.get(reverse('pensioner_courses'))
        self.assertContains(response, '<div class="pagination">')
        self.assertContains(response, '<a class="page_link" href="?page={}">utolsó &raquo;</a>'.format(
            PAGINATION_PAGES + 1))
        self.assertNotContains(response, '<a class="page_link" href="?page=1">&laquo; első</a>')

        response = self.client.get(reverse('pensioner_courses'), {'page': PAGINATION_PAGES + 1})
        self.assertContains(response, '<div class="pagination">')
        self.assertNotContains(response, '<a class="page_link" href="?page={}">utolsó &raquo;</a>'.format(
            PAGINATION_PAGES + 1))
        self.assertContains(response, '<a class="page_link" href="?page=1">&laquo; első</a>')

        for i in range(COURSES_PER_PAGE):
            self._create_course(str((COURSES_PER_PAGE * PAGINATION_PAGES + 1) + i + 1))
        response = self.client.get(reverse('pensioner_courses'), {'page': math.ceil(PAGINATION_PAGES / 2)})
        self.assertContains(response, '<div class="pagination">')
        self.assertContains(response, '<a class="page_link" href="?page={}">utolsó &raquo;</a>'.format(
            PAGINATION_PAGES + 2))
        self.assertContains(response, '<a class="page_link" href="?page=1">&laquo; első</a>')


class ApplyViewTestCase(TestCase):
    """
    Test cases for the Apply view.
    """

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='user', password='test_password')
        self.course = self._create_new_course()

    def _login(self):
        """Logs in a normal user."""
        self.client.logout()
        self.client.force_login(user=self.user)

    def _create_new_course(self, course_number=''):
        course_attrs = {
            'name': 'course_name{}'.format(course_number),
            'price': 10000,
            'description': '*one*two*three',
            'duration': '3 times 90 minutes',
            'for_pensioners': True,
            'for_non_pensioners': True,
            'active': True
        }
        return Course.objects.create(**course_attrs)

    def test_01_apply_rendering(self):
        """Tests that the apply view is rendered successfully and the correct template is used."""
        self._login()
        response = self.client.get(reverse('apply', args=(self.course.slug,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'apply.html')

    def test_02_apply_when_not_logged_in(self):
        """Tests that the apply view is not available for users not logged in."""
        self.client.logout()
        response = self.client.get(reverse('apply', args=(self.course.slug,)))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('apply', args=(self.course.slug,)))

    def test_03_apply_available_only_with_mandatory_fields(self):
        """Tests that the apply view is not available without certain data."""
        self._login()
        self.client.get(reverse('apply', args=(self.course.slug,)))
        mandatory_fields = ['age', 'address']
        optional_fields = ['experience', 'phone_number']
        post_data = {'first_name': 'first_name',
                     'last_name': 'last_name',
                     'age': 50,
                     'address': 'address',
                     'email': 'something@mail.com',
                     'phone_number': '0036301234567',
                     'experience': 'This is the experience.',
                     'course': self.course.name
                     }
        for field in mandatory_fields:
            cur_post_data = post_data.copy()
            del cur_post_data[field]
            response = self.client.post(reverse('apply', args=(self.course.slug,)), cur_post_data)
            self.assertContains(response, '<ul class="error_list">')
            self.assertContains(response, 'Ennek a mezőnek a megadása kötelező.')
            self.assertNotContains(response, 'Jelentkezésed sikeres volt.')
        for field in optional_fields:
            cur_post_data = post_data.copy()
            del cur_post_data[field]
            response = self.client.post(reverse('apply', args=(self.course.slug,)), cur_post_data, follow=True)
            self.assertNotContains(response, '<ul class="error_list">')
            self.assertNotContains(response, 'Ennek a mezőnek a megadása kötelező.')
            self.assertContains(response, 'Jelentkezésed sikeres volt.')


class PrivacyNoticePageViewTestCase(TestCase):
    """
    Test cases for the Privacy Policy view.
    """

    def test_01_privacy_policy_rendering(self):
        """Tests that the Privacy Policy view is rendered successfully and the correct template is used."""
        response = self.client.get(reverse('privacy_notice'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'privacy_notice.html')
