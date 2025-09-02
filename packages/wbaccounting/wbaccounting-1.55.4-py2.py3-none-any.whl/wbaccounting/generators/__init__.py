from django.conf import settings

from .base import AbstractBookingEntryGenerator

if settings.DEBUG:
    from .base import TestGenerator
