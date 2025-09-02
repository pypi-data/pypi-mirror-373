import random
from datetime import date, timedelta
from decimal import Decimal

import factory
from wbcore.contrib.currency.models import CurrencyFXRates
from wbfdm.factories import InstrumentPriceFactory

from wbportfolio.models import AssetPosition


def get_weekday(o):
    instrument = o.underlying_quote or o.underlying_instrument
    if instrument.id and instrument.assets.exists():
        latest_position = instrument.assets.latest("date").date
    else:
        latest_position = date(2020, 1, 1)

    latest_position += timedelta(days=1)
    while latest_position.weekday() > 4:
        latest_position += timedelta(days=1)

    return latest_position


class AssetPositionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AssetPosition
        django_get_or_create = ("portfolio", "underlying_quote", "date", "portfolio_created")

    underlying_instrument = factory.SubFactory("wbfdm.factories.instruments.InstrumentFactory")
    underlying_quote = factory.LazyAttribute(lambda o: o.underlying_instrument)

    date = factory.LazyAttribute(lambda o: get_weekday(o))
    asset_valuation_date = factory.LazyAttribute(lambda o: o.date)

    initial_price = factory.Faker("pydecimal", min_value=100, max_value=120, right_digits=4)
    underlying_quote_price = factory.LazyAttribute(
        lambda o: InstrumentPriceFactory.create(
            instrument=o.underlying_instrument or o.underlying_quote,
            calculated=False,
            date=o.date,
            net_value=o.initial_price,
        )
    )

    initial_shares = factory.LazyAttribute(lambda o: Decimal(random.randint(10, 10000)))
    initial_currency_fx_rate = Decimal(1)
    weighting = factory.Faker("pydecimal", min_value=0.01, max_value=1.0, right_digits=4)

    portfolio = factory.SubFactory("wbportfolio.factories.portfolios.PortfolioFactory")
    portfolio_created = None

    currency = factory.LazyAttribute(lambda o: (o.underlying_instrument or o.underlying_quote).currency)
    currency_fx_rate_instrument_to_usd = factory.LazyAttribute(
        lambda o: CurrencyFXRates.objects.get_or_create(
            currency=o.currency, date=o.date, defaults={"value": Decimal(1.0)}
        )[0]
    )

    is_estimated = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if (asset_valuation_date := kwargs.get("asset_valuation_date", None)) and (
            currency := kwargs.get("currency", None)
        ):
            kwargs["currency_fx_rate_instrument_to_usd"] = CurrencyFXRates.objects.get_or_create(
                date=asset_valuation_date, currency=currency, defaults={"value": 1.0}
            )[0]
        if (asset_valuation_date := kwargs.get("asset_valuation_date", None)) and (
            portfolio := kwargs.get("portfolio", None)
        ):
            kwargs["currency_fx_rate_portfolio_to_usd"] = CurrencyFXRates.objects.get_or_create(
                date=asset_valuation_date, currency=portfolio.currency, defaults={"value": 1.0}
            )[0]
        return super()._create(model_class, *args, **kwargs)

    # @factory.pre
    # def generate_currency_rates(self, create, extracted, **kwargs):
    #
