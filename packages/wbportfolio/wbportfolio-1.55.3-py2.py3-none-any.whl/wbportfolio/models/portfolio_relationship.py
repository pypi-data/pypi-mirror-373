from contextlib import suppress

from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from wbcore.signals import pre_merge
from wbfdm.models import Instrument


class PortfolioBankAccountThroughModel(models.Model):
    class PortfolioBankAccountType(models.TextChoices):
        CASH = "CASH", "Cash"
        SECURITIES = "SECURITIES", "Securities"

    portfolio = models.ForeignKey(
        to="wbportfolio.Portfolio", on_delete=models.CASCADE, related_name="bank_account_through"
    )
    bank_account = models.ForeignKey(
        to="directory.BankingContact", on_delete=models.CASCADE, related_name="portfolio_through"
    )

    portfolio_bank_account_type = models.CharField(
        max_length=255, choices=PortfolioBankAccountType.choices, default=PortfolioBankAccountType.CASH
    )

    def __str__(self) -> str:
        return f"{self.bank_account}: {self.portfolio} ({self.PortfolioBankAccountType[self.portfolio_bank_account_type].label})"

    class Meta:
        verbose_name = "Portfolio Bank Account"
        verbose_name_plural = "Portfolio Bank Accounts"

        constraints = [
            # Each portfolio and bank account can only be connected once
            models.UniqueConstraint(
                fields=["portfolio", "bank_account"],
                name="unique_portfolio_bank_account",
            ),
            # Each portfolio can only have one bank account to hold the securities
            models.UniqueConstraint(
                fields=["portfolio"],
                name="unique_portfolio_bank_account_type",
                condition=Q(portfolio_bank_account_type="SECURITIES"),
            ),
        ]


class InstrumentPortfolioThroughModel(models.Model):
    instrument = models.ForeignKey(
        "wbfdm.Instrument",
        on_delete=models.CASCADE,
        related_name="through_portfolios",
    )
    portfolio = models.ForeignKey(
        "wbportfolio.Portfolio", on_delete=models.CASCADE, related_name="through_instruments"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["instrument"], name="unique_instrument"),
            models.UniqueConstraint(fields=["instrument", "portfolio"], name="unique_portfolio_relationship"),
        ]

    @classmethod
    def get_portfolio(cls, instrument):
        with suppress(InstrumentPortfolioThroughModel.DoesNotExist):
            return InstrumentPortfolioThroughModel.objects.get(instrument=instrument).portfolio

    @classmethod
    def get_primary_portfolio(cls, instrument):
        if portfolio := cls.get_portfolio(instrument):
            if primary_portfolio := portfolio.primary_portfolio:
                return primary_portfolio
            return portfolio


class PortfolioInstrumentPreferredClassificationThroughModel(models.Model):
    portfolio = models.ForeignKey(
        "wbportfolio.Portfolio", on_delete=models.CASCADE, related_name="preferred_classification_instruments"
    )
    instrument = models.ForeignKey(
        "wbfdm.Instrument",
        on_delete=models.CASCADE,
        related_name="preferred_classification_portfolio",
        limit_choices_to=(models.Q(instrument_type__is_classifiable=True) & models.Q(level=0)),
    )
    classification = models.ForeignKey(
        "wbfdm.Classification",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="preferred_classification_throughs",
    )
    classification_group = models.ForeignKey(
        "wbfdm.ClassificationGroup",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="preferred_classification_group_throughs",
    )

    def save(self, *args, **kwargs) -> None:
        if not self.classification_group and self.classification:
            self.classification_group = self.classification.group
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Portfolio Prefered Classification Per Instrument"
        verbose_name_plural = "Portfolio Prefered Classification Per Instruments"
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "instrument", "classification_group"],
                name="unique_prefered_classification_relationship",
            ),
        ]


@receiver(pre_merge, sender="wbfdm.Instrument")
def pre_merge_instrument(sender: models.Model, merged_object: "Instrument", main_object: "Instrument", **kwargs):
    """
    Reassign all merged instrument preferred classification relationship to the main instrument
    """
    for through in PortfolioInstrumentPreferredClassificationThroughModel.objects.filter(instrument=merged_object):
        if classification := through.classification:
            PortfolioInstrumentPreferredClassificationThroughModel.objects.get_or_create(
                portfolio=through.portfolio,
                instrument=main_object,
                classification_group=(
                    through.classification_group if through.classification_group else classification.group
                ),
                defaults={"classification": classification},
            )
        through.delete()
