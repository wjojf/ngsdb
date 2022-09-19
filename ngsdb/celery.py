from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab
from exp.utils import refresh_experiments
import os 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ngsdb.settings')

app = Celery('ngsdb')
app.config_from_object('django.cong:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Executes every Monday morning at 7:30 a.m.
    'add-every-monday-morning': {
        'task': 'tasks.update_experiments',
        'schedule': crontab(hour=7, minute=30, day_of_week=1)
    },
}

@app.task(bind=True)
def update_exeperiments(self):
    refresh_experiments()
    with open('debug.txt', 'a') as f:
        f.write('Experiments updated!')