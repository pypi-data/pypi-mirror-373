from django.db import models
from wbcore.contrib.io.mixins import ImportMixin

from wbportfolio.import_export.handlers.dividend import DividendImportHandler

from .transactions import TransactionMixin


class DividendTransaction(TransactionMixin, ImportMixin, models.Model):
    import_export_handler_class = DividendImportHandler

    class DistributionMethod(models.TextChoices):
        PAYMENT = "Payment", "Payment"
        REINVESTMENT = "Reinvestment", "Reinvestment"

    ex_date = models.DateField(
        verbose_name="Ex-Dividend Date",
        help_text="The date on which the stock starts trading without the dividend",
    )
    record_date = models.DateField(
        verbose_name="Record Date",
        help_text="The date on which the holder must own the shares to be eligible for the dividend",
    )
    distribution_method = models.CharField(
        max_length=255, verbose_name="Type", choices=DistributionMethod.choices, default=DistributionMethod.PAYMENT
    )
    retrocession = models.FloatField(default=1)
    price = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        help_text="The amount paid per share",
        verbose_name="DPS",
    )
    total_value_gross = models.GeneratedField(
        expression=models.F("price") * models.F("shares") * models.F("retrocession"),
        output_field=models.DecimalField(
            max_digits=20,
            decimal_places=4,
        ),
        db_persist=True,
    )

    def save(self, *args, **kwargs):
        if not self.record_date and self.ex_date:
            self.record_date = self.ex_date
        elif self.record_date and not self.ex_date:
            self.ex_date = self.record_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.total_value} - {self.value_date:%d.%m.%Y} : {str(self.underlying_instrument)} (in {str(self.portfolio)})"
