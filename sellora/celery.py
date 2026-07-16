import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sellora.settings")

app = Celery("sellora")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-abandoned-carts-every-15-min": {
        "task": "cart.tasks.check_abandoned_carts",
        "schedule": crontab(minute="*/15"),
    },
}