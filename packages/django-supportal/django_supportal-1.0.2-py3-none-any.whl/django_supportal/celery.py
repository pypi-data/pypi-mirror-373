import os

from celery import Celery

# set the default django settings module for the 'celery' program
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_supportal.settings")

app = Celery("django_supportal")

# using a string here means the worker doesn't have to serialize
# the configuration object to child processes
app.config_from_object("django.conf:settings", namespace="CELERY")

# load task modules from all registered django app configs
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"request: {self.request!r}")
