from decimal import Decimal

from django.db import models


class TransactionMixin(models.Model):
    value_date = models.DateField(
        verbose_name="Value Date",
        help_text="The date that this transaction was valuated/paid.",
    )
    portfolio = models.ForeignKey(
        "wbportfolio.Portfolio", related_name="%(class)ss", on_delete=models.PROTECT, verbose_name="Portfolio"
    )
    underlying_instrument = models.ForeignKey(
        to="wbfdm.Instrument",
        related_name="%(class)ss",
        limit_choices_to=models.Q(children__isnull=True),
        on_delete=models.PROTECT,
        verbose_name="Underlying Instrument",
        help_text="The instrument that is this transaction.",
    )
    currency = models.ForeignKey(
        "currency.Currency",
        related_name="%(class)ss",
        on_delete=models.PROTECT,
        verbose_name="Currency",
    )
    currency_fx_rate = models.DecimalField(
        max_digits=14, decimal_places=8, default=Decimal(1.0), verbose_name="FOREX rate"
    )
    price = models.DecimalField(
        max_digits=16,
        decimal_places=4,
        help_text="The price per share.",
        verbose_name="Price",
    )
    price_gross = models.DecimalField(
        max_digits=16,
        decimal_places=4,
        help_text="The gross price per share.",
        verbose_name="Gross Price",
    )
    shares = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=Decimal("0.0"),
        help_text="The number of shares held at record date, used to calculate the dividend",
        verbose_name="Shares / Quantity",
    )
    fees = models.GeneratedField(
        expression=models.F("price_gross") - models.F("price"),
        output_field=models.DecimalField(
            max_digits=20,
            decimal_places=4,
        ),
        db_persist=True,
    )
    total_value_gross = models.GeneratedField(
        expression=models.F("price_gross") * models.F("shares"),
        output_field=models.DecimalField(
            max_digits=20,
            decimal_places=4,
        ),
        db_persist=True,
    )
    total_value = models.GeneratedField(
        expression=models.F("price") * models.F("shares"),
        output_field=models.DecimalField(
            max_digits=20,
            decimal_places=4,
        ),
        db_persist=True,
    )
    total_value_fx_portfolio = models.GeneratedField(
        expression=models.F("currency_fx_rate") * models.F("price") * models.F("shares"),
        output_field=models.DecimalField(
            max_digits=20,
            decimal_places=4,
        ),
        db_persist=True,
    )
    total_value_gross_fx_portfolio = models.GeneratedField(
        expression=models.F("currency_fx_rate") * models.F("price_gross") * models.F("shares"),
        output_field=models.DecimalField(
            max_digits=20,
            decimal_places=4,
        ),
        db_persist=True,
    )

    comment = models.TextField(default="", verbose_name="Comment", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def pre_save(self):
        if self.underlying_instrument:
            self.currency = self.underlying_instrument.currency

        if self.price is not None and self.price_gross is None:
            self.price_gross = self.price
        elif self.price_gross is not None and self.price is None:
            self.price = self.price_gross

    def save(self, *args, **kwargs):
        self.pre_save()
        if self.currency_fx_rate is None:
            self.currency_fx_rate = self.underlying_instrument.currency.convert(
                self.value_date, self.portfolio.currency, exact_lookup=True
            )
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
