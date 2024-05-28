from django.utils.translation import gettext_lazy as _


# Constants for the application

# regular expression to validate the phone number (of Hungary)
PHONE_NUMBER_VALIDATOR = r'^$|(?:0036|\+36|06)[0-9]{1,10}$'

# pagination constants
PAGINATION_PAGES = 5  # should be an odd number
COURSES_PER_PAGE = 12

# Email templates
USER_CANCELLATION_EMAIL_SUBJECT = str(_('Deaktiváltuk a fiókodat'))
USER_REGISTRATION_EMAIL_SUBJECT = str(_('Erősítsd meg a regisztrációdat a Képzés Mindenkinek! oldalán'))
CALLBACK_EMAIL_SUBJECT = str(_('Valaki visszahívást kért'))
APPLICATION_EMAIL_SUBJECT = str(_('Valaki jelentkezett egy tanfolyamodra'))
