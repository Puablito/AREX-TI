import os
from celery import Celery
from . import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AREXTI_DJANGO.settings')

app = Celery('AREXTI_DJANGO')
# app.config_from_object('django.conf:settings', namespace='CELERY') Celery 4.3
app.config_from_object('django.conf:settings')
# app.autodiscover_tasks() Celery 4.3
app.autodiscover_tasks(settings.INSTALLED_APPS)
