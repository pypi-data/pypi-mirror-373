from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule
from django.db import DEFAULT_DB_ALIAS
from django.apps import apps as global_apps


def initialize_task(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
    # Automatically register the utility periodic tasks
    PeriodicTask.objects.get_or_create(
        task="wbhuman_resources.tasks.create_future_public_holiday",
        defaults={
            "name": "HR: Create future public holiday",
            "crontab": CrontabSchedule.objects.get_or_create(
                minute="0",
                hour="6",
                day_of_month="1",
                month_of_year="*",
                day_of_week="*",
            )[
                0
            ],  # every first of the month at 6am utc
            "interval": None,
        },
    )
