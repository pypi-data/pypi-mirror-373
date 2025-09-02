import factory

from wbportfolio.factories.portfolios import PortfolioFactory
from wbportfolio.models import PortfolioCashTarget


class PortfolioCashTargetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PortfolioCashTarget

    valid_date = factory.Faker("date_object")
    portfolio = factory.SubFactory(PortfolioFactory)
    min_target = factory.Faker("pydecimal", left_digits=0, right_digits=4, max_value=0.01)
    target = factory.Faker("pydecimal", left_digits=0, right_digits=4, max_value=0.01)
    max_target = factory.Faker("pydecimal", left_digits=0, right_digits=4, min_value=0.01)
    comment = factory.Faker("paragraph", nb_sentences=1)
