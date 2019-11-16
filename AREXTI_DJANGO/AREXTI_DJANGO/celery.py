import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AREXTI_DJANGO.settings')

app = Celery('AREXTI_DJANGO')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()