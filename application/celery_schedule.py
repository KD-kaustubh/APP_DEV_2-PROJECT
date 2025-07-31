from celery.schedules import crontab
from application.task import daily_reminder, monthly_report
from flask import current_app

def setup_periodic_tasks():
    celery_app = current_app.extensions['celery']
    
    celery_app.conf.beat_schedule = {
        'daily-reminder': {
            'task': 'daily_reminder',
            'schedule': crontab(hour=10, minute=50),
        },
        'monthly-report': {
            'task': 'monthly_report',
            'schedule': crontab( hour=10, minute=56),
        },
    }
    celery_app.conf.timezone = 'Asia/Kolkata'