import logging
from django.conf import settings


logger = logging.getLogger('hajni_courses_logger')

if settings.TEST_MODE:
    logging.disable(logging.CRITICAL)
