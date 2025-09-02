from django.apps import AppConfig
from django.db.models.signals import post_migrate
from wbcore.contrib.directory.configurations import configuration_registry


class WbportfolioDirectoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wbportfolio.contrib.company_portfolio"

    def ready(self) -> None:
        from .management import initialize_task

        post_migrate.connect(
            initialize_task,
            dispatch_uid="wbportfolio.contrib.company_portfolio.tasks.initialize_task",
        )

        configuration_registry.DEFAULT_COMPANY_MODEL_VIEWSET = (
            "wbportfolio.contrib.company_portfolio.viewsets.CompanyModelViewSet"
        )
        configuration_registry.DEFAULT_COMPANY_MODEL_SERIALIZER = (
            "wbportfolio.contrib.company_portfolio.serializers.CompanyModelSerializer"
        )
        configuration_registry.DEFAULT_PERSON_MODEL_VIEWSET = (
            "wbportfolio.contrib.company_portfolio.viewsets.PersonModelViewSet"
        )
        configuration_registry.DEFAULT_PERSON_MODEL_SERIALIZER = (
            "wbportfolio.contrib.company_portfolio.serializers.PersonModelSerializer"
        )
