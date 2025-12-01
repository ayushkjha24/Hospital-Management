from celery import Celery
from celery.schedules import crontab

# Create Celery instance with Redis as broker + backend
celery = Celery(
    __name__,
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

def init_celery(app):
    # Load Flask config into Celery
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            # Ensure tasks run inside Flask app context
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    # Celery Beat schedules
    celery.conf.beat_schedule = {
        "daily-reminders-every-day-08": {
            "task": "controller.jobs.daily_reminder.send_daily_reminders",
            "schedule": crontab(hour=8, minute=0),
        },
        "monthly-reports-first-day-06": {
            "task": "controller.jobs.monthly_report.create_and_send_monthly_reports",
            "schedule": crontab(day_of_month='1', hour=6, minute=0),
        },
    }

@celery.task
def add_numbers(a, b):
    print("Executing Celery task...")
    return a + b
