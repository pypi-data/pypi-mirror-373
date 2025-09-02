import factory
from faker import Faker

from wbportfolio.factories.portfolios import PortfolioFactory
from wbportfolio.models import DailyPortfolioCashFlow

fake = Faker()


class DailyPortfolioCashFlowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DailyPortfolioCashFlow

    value_date = factory.Faker("date")
    portfolio = factory.SubFactory(PortfolioFactory)

    total_assets = factory.Faker("pydecimal", left_digits=7, right_digits=4, min_value=0.01)
    cash = factory.Faker("pydecimal", left_digits=7, right_digits=4, min_value=0.01)
    cash_flow_forecast = factory.LazyAttribute(lambda o: fake.pydecimal(min_value=0.01, max_value=o.total_assets))

    pending = factory.Faker("pybool")
