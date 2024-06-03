import threading
from django.db import models
from django.db.utils import Error
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _

from hajni_courses.logger import logger
from hajni_courses.utils import HajniCoursesEmail
from hajni_courses_app.utils.constants import PHONE_NUMBER_VALIDATOR, USER_CANCELLATION_EMAIL_SUBJECT, \
    USER_REGISTRATION_EMAIL_SUBJECT, CALLBACK_EMAIL_SUBJECT, APPLICATION_EMAIL_SUBJECT, APPLICATION_CONFIRMATION_SUBJECT
from hajni_courses_app.utils.AccountActivationTokenGenerator import account_activation_token


class CustomUser(AbstractUser):
    """
    CustomUser inherits from AbstractUser from Django's authentication package. We extend the existing model
    with the phone number.
    """
    phone_number = models.CharField(max_length=20, validators=[RegexValidator(regex=PHONE_NUMBER_VALIDATOR,
                                                                              message=_('Adjon meg egy érvényes telefonszámot!'))])

    @staticmethod
    def send_callback_request(self):
        superusers_emails = CustomUser.objects.filter(is_superuser=True).values_list('email', flat=True)
        html_message = render_to_string('emails/callback_request.html', {'user': self})
        email = HajniCoursesEmail(to=superusers_emails, subject=str(_(CALLBACK_EMAIL_SUBJECT)),
                                  message=html_message)
        threading.Thread(target=email.send).start()

    def send_activation_link(self, domain: str, protocol: str):
        """
        Sends the activation link to the user's email.
        """
        email_context = {'username': self.username,
                         'domain': domain,
                         'uid': urlsafe_base64_encode(force_bytes(self.pk)),
                         'token': account_activation_token.make_token(self),
                         'protocol': protocol}
        html_message = render_to_string('emails/user_registration.html', email_context)
        email = HajniCoursesEmail(to=[self.email], subject=str(_(USER_REGISTRATION_EMAIL_SUBJECT)),
                                  message=html_message)
        threading.Thread(target=email.send).start()

    def cancel_user(self) -> bool:
        """
        Cancels the user by putting the is_active flag to False. The user is notified via email.
        """
        try:
            self.is_active = False
            self.save()
            html_message = render_to_string('emails/user_cancellation.html', {'username': self.username})
            email = HajniCoursesEmail(to=self.email, subject=str(_(USER_CANCELLATION_EMAIL_SUBJECT)),
                                      message=html_message)
            threading.Thread(target=email.send).start()
            return True
        except Error:
            logger.error('An error happened during the cancellation of the user {}'.format(self.pk, self.username))
            return False


class Course(models.Model):
    """
    Course model.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, null=False)
    price = models.PositiveIntegerField(null=False)
    description = models.TextField(null=False)
    duration = models.CharField(max_length=150)
    extra_info = models.TextField(null=False)
    for_pensioners = models.BooleanField(default=True)
    for_non_pensioners = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Overriding the save method to populate the slug.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @staticmethod
    def send_application(application_data):
        # email to the admin
        superusers_emails = CustomUser.objects.filter(is_superuser=True).values_list('email', flat=True)
        html_message = render_to_string('emails/application.html', {'first_name': application_data['first_name'],
                                                                    'last_name': application_data['last_name'],
                                                                    'age': application_data['age'],
                                                                    'address': application_data['address'],
                                                                    'email': application_data['email'],
                                                                    'phone_number': application_data['phone_number'],
                                                                    'experience': application_data['experience'],
                                                                    'course': application_data['course']
                                                                    })
        email = HajniCoursesEmail(to=superusers_emails, subject=str(_(APPLICATION_EMAIL_SUBJECT)),
                                  message=html_message)
        threading.Thread(target=email.send).start()

        # email to the user
        html_message = render_to_string('emails/application_confirmation.html',
                                        {'first_name': application_data['first_name'],
                                         'course': application_data['course']
                                         })
        email = HajniCoursesEmail(to=application_data['email'], subject=str(_(APPLICATION_CONFIRMATION_SUBJECT)),
                                  message=html_message)
        threading.Thread(target=email.send).start()
