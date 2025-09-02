from datetime import date

import factory
from psycopg.types.range import DateRange

from wbportfolio.models import (
    InstrumentPortfolioThroughModel,
    Portfolio,
    PortfolioPortfolioThroughModel,
)


class PortfolioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Portfolio

    name = factory.Sequence(lambda n: f"Portfolio {n}")
    currency = factory.SubFactory("wbcore.contrib.currency.factories.CurrencyUSDFactory")
    is_manageable = True
    is_tracked = True
    is_lookthrough = False
    only_weighting = True
    invested_timespan = DateRange(date.min, date.max)

    @factory.post_generation
    def depends_on(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for portfolio in extracted:
                self.depends_on.add(portfolio)


class ModelPortfolioFactory(PortfolioFactory):
    @factory.post_generation
    def dependant_portfolios(self, create, extracted, **kwargs):
        PortfolioPortfolioThroughModel.objects.create(
            portfolio=PortfolioFactory.create(),
            dependency_portfolio=self,
            type=PortfolioPortfolioThroughModel.Type.MODEL,
        )


class InstrumentPortfolioThroughModelFactory(factory.django.DjangoModelFactory):
    instrument = factory.SubFactory("wbportfolio.factories.ProductFactory")
    portfolio = factory.SubFactory("wbportfolio.factories.PortfolioFactory")

    class Meta:
        model = InstrumentPortfolioThroughModel
        django_get_or_create = ("instrument",)
