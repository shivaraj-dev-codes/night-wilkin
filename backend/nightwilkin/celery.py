import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nightwilkin.settings')

app = Celery('nightwilkin')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'auto-end-long-sessions': {
        'task': 'core.tasks.auto_end_long_sessions',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'check-expected-end-times': {
        'task': 'core.tasks.check_expected_end_times',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'check-danger-zones': {
        'task': 'core.tasks.check_danger_zones',
        'schedule': crontab(minute='*/2'),  # Every 2 minutes
    },
    'anonymize-old-locations': {
        'task': 'core.tasks.anonymize_old_locations',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
