import logging
from datetime import date

from dateutil import rrule
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import gettext_lazy as _
from pandas._libs.tslibs.offsets import BDay
from wbcore.utils.importlib import import_from_dotted_path
from wbcore.utils.models import ComplexToStringMixin
from wbcore.utils.rrules import convert_rrulestr_to_dict, humanize_rrule

from wbportfolio.models.orders.order_proposals import OrderProposal
from wbportfolio.models.portfolio import Portfolio
from wbportfolio.pms.typing import Portfolio as PortfolioDTO
from wbportfolio.rebalancing.base import AbstractRebalancingModel

logger = logging.getLogger("pms")


class RebalancingModel(models.Model):
    name = models.CharField(max_length=64, verbose_name="Name")
    class_path = models.CharField(max_length=512, verbose_name="Class path")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Rebalancing Model"
        verbose_name_plural = "Rebalancing Models"

    @cached_property
    def model_class(self) -> type[AbstractRebalancingModel]:
        """
        Return the imported backend class
        Returns:
            The backend class
        """
        return import_from_dotted_path(self.class_path)

    def get_target_portfolio(
        self,
        portfolio: Portfolio,
        trade_date: date,
        last_effective_date: date,
        effective_portfolio: PortfolioDTO | None = None,
        **kwargs,
    ) -> PortfolioDTO:
        model = self.model_class(
            portfolio, trade_date, last_effective_date, effective_portfolio=effective_portfolio, **kwargs
        )
        if not model.is_valid():
            raise ValidationError(model.validation_errors)
        return model.get_target_portfolio()

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbportfolio:rebalancingmodelrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{name}}"


class Rebalancer(ComplexToStringMixin, models.Model):
    portfolio = models.OneToOneField(
        "wbportfolio.Portfolio", on_delete=models.CASCADE, related_name="automatic_rebalancer"
    )
    rebalancing_model = models.ForeignKey(
        RebalancingModel, on_delete=models.PROTECT, related_name="rebalancers", verbose_name="Rebalancing Model"
    )
    parameters = models.JSONField(default=dict, verbose_name="Parameters", blank=True)
    apply_order_proposal_automatically = models.BooleanField(
        default=False, verbose_name="Apply Order Proposal Automatically"
    )
    activation_date = models.DateField(verbose_name="Activation Date")
    frequency = models.CharField(
        default="RRULE:FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=1",
        max_length=256,
        verbose_name=_("Evaluation Frequency"),
        help_text=_("The Evaluation Frequency in RRULE format"),
    )

    def save(self, *args, **kwargs):
        if not self.activation_date:
            try:
                self.activation_date = self.portfolio.assets.earliest("date").date
            except ObjectDoesNotExist:
                self.activation_date = date.today()
        super().save(*args, **kwargs)

    def _get_next_valid_date(self, valid_date: date) -> date:
        pivot_date = valid_date
        while OrderProposal.objects.filter(
            portfolio=self.portfolio, status=OrderProposal.Status.FAILED, trade_date=pivot_date
        ).exists():
            pivot_date = (pivot_date + BDay(1)).date()
        return pivot_date

    def is_valid(self, trade_date: date) -> bool:
        if OrderProposal.objects.filter(
            portfolio=self.portfolio,
            status=OrderProposal.Status.APPLIED,
            trade_date=trade_date,
            rebalancing_model__isnull=True,
        ).exists():  # if a already applied order proposal exists, we do not allow a re-evaluatioon of the rebalancing (only possible if "replayed")
            return False
        for initial_valid_datetime in self.get_rrule(trade_date):
            initial_valid_date = initial_valid_datetime.date()
            alternative_valid_date = self._get_next_valid_date(initial_valid_date)
            if trade_date in [alternative_valid_date, initial_valid_date]:
                return True
            if alternative_valid_date > trade_date:
                break
        return False

    def evaluate_rebalancing(self, trade_date: date, effective_portfolio=None):
        order_proposal, _ = OrderProposal.objects.get_or_create(
            trade_date=trade_date,
            portfolio=self.portfolio,
            defaults={
                "comment": "Automatic rebalancing",
                "rebalancing_model": self.rebalancing_model,
            },
        )
        order_proposal.portfolio = self.portfolio
        if order_proposal.rebalancing_model == self.rebalancing_model:
            try:
                logger.info(
                    f"Getting target portfolio ({self.portfolio}) for rebalancing model {self.rebalancing_model} for trade date {trade_date:%Y-%m-%d}"
                )
                target_portfolio = self.rebalancing_model.get_target_portfolio(
                    self.portfolio,
                    order_proposal.trade_date,
                    order_proposal.value_date,
                    effective_portfolio=effective_portfolio,
                    **self.parameters,
                )
                order_proposal.apply_workflow(
                    apply_automatically=self.apply_order_proposal_automatically,
                    target_portfolio=target_portfolio,
                    effective_portfolio=effective_portfolio,
                )
            except ValidationError as e:
                logger.warning(f"Validation error while approving the orders: {e}")
                # If we encountered a validation error, we set the order proposal as failed
                order_proposal.status = OrderProposal.Status.FAILED
            order_proposal.save()
        return order_proposal

    @property
    def rrule(self):
        return self.get_rrule()

    def get_next_rebalancing_date(self, pivot_date: date) -> date | None:
        for _dt in self.rrule:
            _d = _dt.date()
            if _d > pivot_date:
                return _d

    @property
    def frequency_repr(self):
        return humanize_rrule(self.rrule)

    def get_rrule(self, to_date: date | None = None, count: int | None = None):
        rrule_dict = convert_rrulestr_to_dict(self.frequency, dtstart=self.activation_date, until=to_date, count=count)
        return rrule.rrule(**rrule_dict)

    def compute_str(self):
        return f"{self.frequency_repr} {self.portfolio.name} ({self.rebalancing_model.name})"

    class Meta:
        verbose_name = "Rebalancer"
        verbose_name_plural = "Rebalancers"

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbportfolio:rebalancer"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbportfolio:rebalancerrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"


@receiver(post_migrate, sender=RebalancingModel)
def post_migrate_rebalancing_model(sender, verbosity, interactive, stdout, using, plan, apps, **kwargs):
    autodiscover_modules("rebalancing.models")
