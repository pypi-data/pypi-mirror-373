from datetime import date, timedelta

from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from wbcore.contrib.directory.signals import deactivate_profile
from wbcore.signals import pre_merge
from wbfdm.models import Instrument


class PortfolioRole(models.Model):
    default_error_messages = {
        "manager": "If role type is Manager or Risk Manager, no {model} can be selected.",
        "product_index": "Not both Product and Index can be selected.",
        "start_end": "If a start and end date are selected, then the end date has be after the start date.",
    }

    class RoleType(models.TextChoices):
        MANAGER = "MANAGER", "Manager"
        RISK_MANAGER = "RISK_MANAGER", "Risk Manager"
        PORTFOLIO_MANAGER = "PORTFOLIO_MANAGER", "Portfolio Manager"
        ANALYST = "ANALYST", "Analyst"

    role_type = models.CharField(max_length=24, choices=RoleType.choices, verbose_name="Type")
    person = models.ForeignKey(
        "directory.Person",
        related_name="portfolio_roles",
        on_delete=models.CASCADE,
        verbose_name="Person",
    )

    start = models.DateField(null=True, blank=True, verbose_name="Start")
    end = models.DateField(null=True, blank=True, verbose_name="End")

    instrument = models.ForeignKey(
        "wbfdm.Instrument",
        related_name="portfolio_roles",
        null=True,
        blank=True,
        limit_choices_to=models.Q(children__isnull=True),
        on_delete=models.CASCADE,
        verbose_name="Instrument",
    )

    weighting = models.FloatField(default=1, verbose_name="Weight")

    class Meta:
        verbose_name = "Portfolio Role"
        verbose_name_plural = "Portfolio Roles"

    def __str__(self):
        return f"{self.role_type} {self.person.computed_str}"

    def save(self, *args, **kwargs):
        assert (
            self.role_type in [self.RoleType.MANAGER, self.RoleType.RISK_MANAGER] and not self.instrument
        ) or self.role_type in [
            self.RoleType.PORTFOLIO_MANAGER,
            self.RoleType.ANALYST,
        ], self.default_error_messages["manager"].format(model="instrument")

        assert (self.start and self.end and self.start < self.end) or (
            not self.start or not self.end
        ), self.default_error_messages["start_end"]

        super().save(*args, **kwargs)

    @classmethod
    def is_manager(cls, person):
        """Determines whether a person can access manager things (or is a superuser)

        Arguments:
            person {crm.Person} -- The person to be checked

        Returns:
            bool -- Can manage or not
        """

        today = date.today()

        manager = cls.objects.filter(
            Q(person=person)
            & Q(role_type__in=[cls.RoleType.MANAGER, cls.RoleType.RISK_MANAGER])
            & (Q(start__isnull=True) | Q(start__lte=today))
            & (Q(end__isnull=True) | Q(end__gte=today))
        )

        return person.user_account.is_superuser or manager.exists()

    @classmethod
    def is_portfolio_manager(cls, person, instrument=None, portfolio=None, include_superuser=True):
        """Determines whether a person can access portfolio manager things (or is a superuser/manager)

        Arguments:
            person {crm.Person} -- The person to be checked

        Returns:
            bool -- Can manage or not
        """
        today = date.today()
        manager = cls.objects.filter(
            (
                Q(person=person)
                & Q(role_type__in=[cls.RoleType.PORTFOLIO_MANAGER, cls.RoleType.MANAGER, cls.RoleType.RISK_MANAGER])
            )
            & (Q(start__isnull=True) | Q(start__lte=today))
            & (Q(end__isnull=True) | Q(end__gte=today))
        )

        if instrument:
            manager = manager.filter(
                Q(instrument=instrument)
                | Q(instrument__isnull=True)
                | Q(role_type__in=[cls.RoleType.MANAGER, cls.RoleType.RISK_MANAGER])
            )
        elif portfolio:
            manager = manager.filter(
                Q(instrument__in=portfolio.instruments.all())
                | Q(instrument__isnull=True)
                | Q(role_type__in=[cls.RoleType.MANAGER, cls.RoleType.RISK_MANAGER])
            )

        if include_superuser:
            return person.user_account.is_superuser or manager.exists()
        return manager.exists()

    @classmethod
    def is_analyst(cls, person, instrument=None, portfolio=None, include_superuser=True):
        """Determines whether a person can access analyst things (or is a superuser/manager/portfolio manager)

        Arguments:
            person {crm.Person} -- The person to be checked

        Returns:
            bool -- Can manage or not
        """
        today = date.today()
        manager = cls.objects.filter(
            Q(person=person)
            & (Q(start__isnull=True) | Q(start__lte=today))
            & (Q(end__isnull=True) | Q(end__gte=today))
        )

        if instrument:
            manager = manager.filter(
                Q(instrument=instrument)
                | Q(instrument__isnull=True)
                | Q(role_type__in=[cls.RoleType.PORTFOLIO_MANAGER, cls.RoleType.MANAGER, cls.RoleType.RISK_MANAGER])
            )
        elif portfolio:
            manager = manager.filter(
                Q(instrument__in=portfolio.instruments.all())
                | Q(instrument__isnull=True)
                | Q(role_type__in=[cls.RoleType.PORTFOLIO_MANAGER, cls.RoleType.MANAGER, cls.RoleType.RISK_MANAGER])
            )
        if include_superuser:
            return person.user_account.is_superuser or manager.exists()
        return manager.exists()

    @classmethod
    def portfolio_managers(cls):
        today = date.today()
        return (
            cls.objects.filter(
                Q(role_type=cls.RoleType.PORTFOLIO_MANAGER)
                & (Q(start__isnull=True) | Q(start__lte=today))
                & (Q(end__isnull=True) | Q(end__gte=today))
            )
            .values("person")
            .distinct("person")
        )

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:portfoliorole"


@receiver(deactivate_profile)
def handle_user_deactivation(sender, instance, substitute_profile=None, **kwargs):
    deactivation_date = date.today() - timedelta(days=1)
    for role in PortfolioRole.objects.filter(person=instance, end__isnull=True):
        role.end = deactivation_date
        role.save()
        if (
            substitute_profile
            and not PortfolioRole.objects.filter(
                person=substitute_profile, end__isnull=True, instrument=role.instrument
            ).exists()
        ):
            PortfolioRole.objects.create(
                instrument=role.instrument,
                person=substitute_profile,
                role_type=role.role_type,
                start=deactivation_date,
                weighting=role.weighting,
            )


@receiver(pre_merge, sender="wbfdm.Instrument")
def pre_merge_instrument(sender: models.Model, merged_object: Instrument, main_object: Instrument, **kwargs):
    """
    Simply reassign the portfolio roles linked to the merged instrument to the main instrument
    """
    merged_object.portfolio_roles.update(instrument=main_object)
