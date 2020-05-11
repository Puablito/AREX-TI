import os
from celery import Celery
from . import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AREXTI_DJANGO.settings')

app = Celery('AREXTI_DJANGO')
# app.config_from_object('django.conf:settings', namespace='CELERY') # Celery 4.3 comentar para 4.4
app.config_from_object({"django.conf":settings,
                        "broker_heartbeat":0,
                        "result_backend":'django-db',})  # Celery 3.1.25
# app.autodiscover_tasks() # Celery 4.3
app.autodiscover_tasks(settings.INSTALLED_APPS)  # Celery 3.1.25

