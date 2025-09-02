import factory

from wbportfolio.factories.portfolios import PortfolioFactory
from wbportfolio.models import PortfolioSwingPricing


class PortfolioSwingPricingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PortfolioSwingPricing

    valid_date = factory.Faker("date_object")
    portfolio = factory.SubFactory(PortfolioFactory)
    negative_threshold = factory.Faker("pydecimal", left_digits=0, right_digits=4, min_value=-0.99, max_value=-0.01)
    negative_swing_factor = factory.Faker("pydecimal", left_digits=0, right_digits=4, min_value=-0.99, max_value=-0.01)
    positive_threshold = factory.Faker("pydecimal", left_digits=0, right_digits=4, min_value=0.01, max_value=0.99)
    positive_swing_factor = factory.Faker("pydecimal", left_digits=0, right_digits=4, min_value=0.01, max_value=0.99)
