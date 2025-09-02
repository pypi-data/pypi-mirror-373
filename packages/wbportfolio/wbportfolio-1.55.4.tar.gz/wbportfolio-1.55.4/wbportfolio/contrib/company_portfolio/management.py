from django.apps import apps as global_apps
from django.db import DEFAULT_DB_ALIAS
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from .constants import DEFAULT_PORTFOLIO_DATA_UPDATE_TASK_INTERVAL_MINUTES


def initialize_task(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
    PeriodicTask.objects.update_or_create(
        name="Portfolio: Update Company Portfolio Data",
        defaults={
            "name": "Portfolio: Update Company Portfolio Data",
            "interval": IntervalSchedule.objects.get_or_create(
                every=DEFAULT_PORTFOLIO_DATA_UPDATE_TASK_INTERVAL_MINUTES, period=IntervalSchedule.MINUTES
            )[0],
            "task": "wbportfolio.contrib.company_portfolio.tasks.update_all_portfolio_data",
            "crontab": None,
        },
    )
