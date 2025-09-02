import random

import factory
from wbcore.contrib.directory.factories.entries import CompanyFactory
from wbfdm.factories.instruments import InstrumentFactory, InstrumentTypeFactory

from wbportfolio.factories import ModelPortfolioFactory, PortfolioFactory
from wbportfolio.models import InstrumentPortfolioThroughModel
from wbportfolio.models.products import (
    AssetClass,
    InvestmentIndex,
    LegalStructure,
    Liquidy,
    Product,
    TypeOfReturn,
)


class ProductFactory(InstrumentFactory):
    class Meta:
        model = Product

    share_price = 100
    issue_price = factory.LazyAttribute(lambda o: random.randint(1, 1000))
    bank = factory.SubFactory("wbcore.contrib.directory.factories.CompanyFactory")

    type_of_return = factory.Faker("random_element", elements=[x[0] for x in TypeOfReturn.choices()])
    asset_class = factory.Faker("random_element", elements=[x[0] for x in AssetClass.choices()])
    legal_structure = factory.Faker("random_element", elements=[x[0] for x in LegalStructure.choices()])
    investment_index = factory.Faker("random_element", elements=[x[0] for x in InvestmentIndex.choices()])
    liquidity = factory.Faker("random_element", elements=[x[0] for x in Liquidy.choices()])
    risk_scale = factory.LazyAttribute(lambda o: random.randint(1, 7))

    dividend = factory.Faker("random_element", elements=[x[0] for x in Product.Dividend.choices])
    minimum_subscription = factory.LazyAttribute(lambda o: random.randint(100, 200))

    cut_off_time = factory.Faker("time_object")

    external_webpage = factory.Faker("url")
    instrument_type = factory.LazyAttribute(lambda o: InstrumentTypeFactory.create(name="Product", key="product"))

    @factory.post_generation
    def create_initial_portfolio(product, *args, **kwargs):
        if product.id and not product.portfolios.exists():
            portfolio = PortfolioFactory.create()
            InstrumentPortfolioThroughModel.objects.create(instrument=product, portfolio=portfolio)

    # wbportfolio = factory.SubFactory(PortfolioFactory)
    # portfolio_computed = factory.SubFactory(PortfolioFactory)


class WhiteLabelProductFactory(ProductFactory):
    @factory.post_generation
    def white_label_customers(self, create, extracted, **kwargs):
        if not create:
            return

        num_of_wlc = extracted or 1

        for _ in range(num_of_wlc):
            self.white_label_customers.add(CompanyFactory.create())


class IndexProductFactory(ProductFactory):
    pass


class ModelPortfolioWithBaseProductFactory(ModelPortfolioFactory):
    @factory.post_generation
    def create_instrument(self, create, extracted, **kwargs):
        if create:
            instrument = ProductFactory.create()
            InstrumentPortfolioThroughModel.objects.update_or_create(
                instrument=instrument, defaults={"portfolio": self}
            )
