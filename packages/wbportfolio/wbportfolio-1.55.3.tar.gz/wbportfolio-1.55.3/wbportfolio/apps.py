from django.apps import AppConfig
from django.apps import apps as global_apps
from django.db import DEFAULT_DB_ALIAS
from django.db.models.signals import post_migrate
from django.utils.module_loading import autodiscover_modules


class WbportfolioConfig(AppConfig):
    name = "wbportfolio"

    def ready(self):
        def autodiscover_backends(
            app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs
        ):
            # we wrap the autodiscover into a post_migrate receiver because we expect db calls
            autodiscover_modules("rebalancing")

        post_migrate.connect(
            autodiscover_backends,
            dispatch_uid="wbportfolio.autodiscover_rebalancing",
        )
