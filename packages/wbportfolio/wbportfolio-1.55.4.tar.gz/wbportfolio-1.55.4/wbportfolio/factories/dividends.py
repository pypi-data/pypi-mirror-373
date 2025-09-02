import random

import factory

from wbportfolio.models import DividendTransaction


class DividendTransactionsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DividendTransaction

    currency_fx_rate = 1.0
    portfolio = factory.SubFactory("wbportfolio.factories.PortfolioFactory")
    underlying_instrument = factory.SubFactory("wbfdm.factories.InstrumentFactory")
    currency = factory.SubFactory("wbcore.contrib.currency.factories.CurrencyFactory")
    value_date = factory.Faker("date_object")
    ex_date = factory.Faker("date_object")
    record_date = factory.LazyAttribute(lambda o: o.ex_date)
    retrocession = 1.0
    shares = factory.LazyAttribute(lambda o: random.randint(10, 10000))
    price = factory.LazyAttribute(lambda o: random.randint(10, 10000))
