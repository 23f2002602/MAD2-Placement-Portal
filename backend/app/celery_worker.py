import os

from celery import Celery

from celery.schedules import crontab

from dotenv import load_dotenv

load_dotenv()

def make_celery(flask_app=None):

    celery = Celery(

        'placement_portal',

        broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/2'),

        backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/3'),

        include=[

            'app.tasks.reminders',                              

            'app.tasks.monthly_report',                           

            'app.tasks.export_csv',                          

        ]

    )

    celery.conf.update(

        task_serializer='json',

        accept_content=['json'],

        result_serializer='json',

        timezone='Asia/Kolkata',

        enable_utc=True,

        beat_schedule={

            'daily-reminders': {

                'task': 'app.tasks.reminders.send_daily_reminders',

                'schedule': 60.0 * 60 * 24,                   

            },

            'monthly-report': {

                'task': 'app.tasks.monthly_report.send_monthly_report',

                'schedule': crontab(day_of_month=1, hour=8, minute=0),

            },

        }

    )

    if flask_app is not None:

        class ContextTask(celery.Task):

            def __call__(self, *args, **kwargs):

                with flask_app.app_context():

                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery

celery_app = make_celery()

def init_celery(flask_app):

    class ContextTask(celery_app.Task):

        def __call__(self, *args, **kwargs):

            with flask_app.app_context():

                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask

    for task_name, task in celery_app.tasks.items():

        if not task_name.startswith('celery.'):

            task.__class__ = ContextTask

    return celery_app
