import factory

from wbportfolio.models import Rebalancer, RebalancingModel


class RebalancingModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RebalancingModel

    name = factory.Faker("name")
    class_path = "wbportfolio.rebalancing.models.equally_weighted.EquallyWeightedRebalancing"


class RebalancerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rebalancer

    portfolio = factory.SubFactory("wbportfolio.factories.portfolios.PortfolioFactory")
    rebalancing_model = factory.SubFactory(RebalancingModelFactory)
    parameters = dict()
    apply_order_proposal_automatically = False
    frequency = "RRULE:FREQ=MONTHLY;"
    activation_date = None
