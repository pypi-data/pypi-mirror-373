"""Extends the builtin Django admin interface for the parent application.

Extends and customizes the site-wide administration utility with
interfaces for managing application database constructs.
"""

from django.conf import settings

settings.JAZZMIN_SETTINGS['icons'].update({
    'django_celery_beat.ClockedSchedule': 'fa fa-clock',
    'django_celery_beat.CrontabSchedule': 'fa fa-asterisk',
    'django_celery_beat.IntervalSchedule': 'fa fa-redo',
    'django_celery_beat.SolarSchedule': 'fa fa-sun',
    'django_celery_beat.PeriodicTask': 'fa fa-check',
})

settings.JAZZMIN_SETTINGS['order_with_respect_to'].extend([
    'django_celery_beat.PeriodicTask',
    'django_celery_beat.IntervalSchedule',
    'django_celery_beat.ClockedSchedule',
    'django_celery_beat.CrontabSchedule',
    'django_celery_beat.SolarSchedule',
])
