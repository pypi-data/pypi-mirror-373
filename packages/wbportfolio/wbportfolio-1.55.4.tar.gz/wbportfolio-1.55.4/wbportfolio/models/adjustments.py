import datetime
import logging
import operator
from decimal import Decimal
from functools import reduce
from typing import Optional

import numpy as np
from celery import chain, shared_task
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_fsm import FSMField, transition
from pandas.tseries.offsets import BDay
from wbcore.contrib.authentication.models import User
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.io.mixins import ImportMixin
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton
from wbcore.signals import pre_merge
from wbfdm.models.instruments.instruments import Instrument, import_prices_as_task

from wbportfolio.import_export.handlers.adjustment import AdjustmentImportHandler
from wbportfolio.models.roles import PortfolioRole

logger = logging.getLogger("pms")


class Adjustment(ImportMixin, models.Model):
    import_export_handler_class = AdjustmentImportHandler

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPLIED = "APPLIED", "Applied"
        DENIED = "DENIED", "Denied"

    status = FSMField(default=Status.PENDING, choices=Status.choices, verbose_name="Status")

    date = models.DateField(verbose_name="Executive Date")
    instrument = models.ForeignKey(
        "wbfdm.Instrument",
        on_delete=models.CASCADE,
        related_name="pms_adjustments",
        limit_choices_to=models.Q(("children__isnull", True)),
    )
    factor = models.DecimalField(default=Decimal(1), max_digits=30, decimal_places=17, verbose_name="Factor")
    cumulative_factor = models.DecimalField(
        default=Decimal(1), max_digits=30, decimal_places=17, verbose_name="Cumulative Factor"
    )
    last_handler = models.ForeignKey(
        "directory.Person", blank=True, null=True, on_delete=models.SET_NULL, related_name="last_handled_adjustments"
    )

    def __str__(self) -> str:
        return f"Instrument {str(self.instrument)} (date: {self.date}, factor: {self.factor})"

    @property
    def adjustment_date(self) -> datetime.date:
        return (self.date - BDay(1)).date()

    def save(self, *args, **kwargs):
        if not self.cumulative_factor or self.cumulative_factor == Decimal(1):
            self.cumulative_factor = self.get_cumulative_factor()
        super().save(*args, **kwargs)

    def get_cumulative_factor(self) -> Decimal:
        applied_parent_adjustments_factors = list(
            Adjustment.objects.exclude(id=self.id)
            .filter(status=self.Status.APPLIED, instrument=self.instrument, date__gte=self.date)
            .values_list("factor", flat=True)
        )
        return Decimal(np.prod([*applied_parent_adjustments_factors]))

    def automatically_applied_adjustments_on_assets(self) -> bool:
        return reduce(operator.or_, [1 / self.factor % i == 0 for i in range(2, 5)])

    def apply_adjustment_on_assets(self):
        self.instrument.assets.filter(
            models.Q(date__lte=self.adjustment_date)
            | (models.Q(applied_adjustment__isnull=True) & models.Q(applied_adjustment__date__lt=self.date))
        ).update(applied_adjustment=self)

    def revert_adjustment_on_assets(self):
        self.adjustmented_assets.update(applied_adjustment=None)
        future_adjustments = self.instrument.pms_adjustments.filter(date__gt=self.date)
        if future_adjustments.exists():
            future_adjustments.earliest(
                "date"
            ).apply_adjustment_on_assets()  # We reevalute the next future adjustment in order to check if this one can replace the reverted adjustment
        self.status = self.Status.PENDING
        self.save()

    @transition(
        field=status,
        source=[Status.PENDING],
        target=Status.APPLIED,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(user.profile),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:adjustment",),
                icon=WBIcon.APPROVE.icon,
                key="apply",
                label="Apply",
                action_label="Apply",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def apply(self, by: Optional["User"] = None, description: Optional[str] = None, **kwargs):
        if profile := getattr(by, "profile", None):
            self.last_handler = profile
        apply_adjustment_on_assets_as_task.delay(self.id)

    @transition(
        field=status,
        source=[Status.PENDING],
        target=Status.DENIED,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(user.profile),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:adjustment",),
                icon=WBIcon.DENY.icon,
                key="deny",
                label="Deny",
                action_label="Deny",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def deny(self, by=None, description=None, **kwargs):
        if profile := getattr(by, "profile", None):
            self.last_handler = profile

    @transition(
        field=status,
        source=[Status.APPLIED],
        target=Status.PENDING,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(user.profile),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:adjustment",),
                icon=WBIcon.UNDO.icon,
                key="revert",
                label="Revert",
                action_label="Revert",
            )
        },
    )
    def revert(self, by=None, description=None, **kwargs):
        if profile := getattr(by, "profile", None):
            self.last_handler = profile
        revert_adjustment_on_assets_as_task.delay(self.id)

    def import_instrument_prices(self):
        # If the adjusted instrument is not within any portfolio, we automatically approve (and applied) the adjustments
        # We reimport prices when a adjustment comes in, not really the most efficient but at least, we are sure we keep having corrected price
        chain(
            import_prices_as_task.si(self.instrument.id, clear=True),
            post_adjustment_on_prices.si(self.id, automatically_confirm_approve_adjustment_on_assets=True),
        ).apply_async()

    class Meta:
        verbose_name = "Datum Adjustment"
        verbose_name_plural = "Data Adjustment"
        constraints = [
            models.UniqueConstraint(
                fields=["date", "instrument"],
                name="unique_date_instrument",
            ),
        ]
        indexes = [
            models.Index(
                name="instrument_adjustment_idx",
                fields=["instrument", "-date"],
            )
        ]

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:adjustment"


# Shared tasks


@shared_task(queue="portfolio")
def apply_adjustment_on_assets_as_task(adjustment_id):
    adjustment = Adjustment.objects.get(id=adjustment_id)
    adjustment.apply_adjustment_on_assets()


@shared_task(queue="portfolio")
def revert_adjustment_on_assets_as_task(adjustment_id):
    adjustment = Adjustment.objects.get(id=adjustment_id)
    adjustment.revert_adjustment_on_assets()


@shared_task(queue="portfolio")
def post_adjustment_on_prices(adjustment_id, automatically_confirm_approve_adjustment_on_assets: bool | None = False):
    # We just notified the concerned users that a adjustment has been processed, prices have been reimported and as there
    # are assets on the instrument, manually confirmation is needed before apply the adjustment
    adjustment = Adjustment.objects.get(id=adjustment_id)
    if adjustment.instrument.assets.filter(date__lte=adjustment.date).exists():
        if (
            adjustment.automatically_applied_adjustments_on_assets()
            or automatically_confirm_approve_adjustment_on_assets
        ):
            adjustment.apply_adjustment_on_assets()
            adjustment.status = Adjustment.Status.APPLIED
        else:
            for user in User.objects.filter(profile__in=PortfolioRole.portfolio_managers()):
                send_notification(
                    code="wbportfolio.adjustment.add",
                    title="A new adjustment was imported",
                    body=f"A adjustment for {str(adjustment.instrument)} with ex Date  {adjustment.date} and factor {adjustment.factor} was imported. Please confirm (to apply) or deny it.",
                    user=user,
                    reverse_name="wbportfolio:adjustment-detail",
                    reverse_args=[adjustment.id],
                )
    else:
        adjustment.status = Adjustment.Status.APPLIED
    adjustment.save()


# Receivers


@receiver(post_delete, sender=Adjustment)
def post_delete_adjustment(sender, instance, **kwargs):
    for adjustment in Adjustment.objects.filter(instrument=instance.instrument).order_by("date"):
        adjustment.save()


@receiver(post_save, sender="wbportfolio.Adjustment")
def post_save_adjustment(sender, instance, created, raw, **kwargs):
    if created and (instance.instrument.assets.exists() or instance.instrument.prices.exists()):
        instance.import_instrument_prices()


@receiver(pre_merge, sender="wbfdm.Instrument")
def pre_merge_instrument(sender: models.Model, merged_object: "Instrument", main_object: "Instrument", **kwargs):
    """
    Simply reassign the adjustments of the merged instrument to the main instrument if they don't already exist for that day, otherwise simply delete them
    """
    merged_object.pms_adjustments.annotate(
        already_exists=models.Exists(Adjustment.objects.filter(date=models.OuterRef("date"), instrument=main_object))
    ).filter(already_exists=True).delete()
    merged_object.pms_adjustments.update(instrument=main_object)
