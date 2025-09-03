"""The backend REST API for the Keystone web platform."""

import os

from .apps.scheduler.celery import celery_app

# Default to using the packaged application settings file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'keystone_api.main.settings')

# Including the celery application object in __all__ is a celery requirement
# and ensures shared tasks use the appropriate celery instance.
__all__ = ('celery_app', 'apps')
