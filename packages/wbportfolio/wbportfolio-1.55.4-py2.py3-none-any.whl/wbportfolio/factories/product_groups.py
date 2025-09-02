import factory
from wbfdm.factories.instruments import InstrumentFactory

from wbportfolio.factories import PortfolioFactory
from wbportfolio.models import InstrumentPortfolioThroughModel, ProductGroup, ProductGroupRepresentant


class ProductGroupFactory(InstrumentFactory):
    class Meta:
        model = ProductGroup

    type = factory.Faker("random_element", elements=[x[0] for x in ProductGroup.ProductGroupType.choices])
    category = factory.Faker("random_element", elements=[x[0] for x in ProductGroup.ProductGroupCategory.choices])
    umbrella = factory.Faker("company")
    management_company = factory.SubFactory("wbcore.contrib.directory.factories.entries.CompanyFactory")
    depositary = factory.SubFactory("wbcore.contrib.directory.factories.entries.CompanyFactory")
    transfer_agent = factory.SubFactory("wbcore.contrib.directory.factories.entries.CompanyFactory")
    administrator = factory.SubFactory("wbcore.contrib.directory.factories.entries.CompanyFactory")
    investment_manager = factory.SubFactory("wbcore.contrib.directory.factories.entries.CompanyFactory")
    auditor = factory.SubFactory("wbcore.contrib.directory.factories.entries.CompanyFactory")
    paying_agent = factory.SubFactory("wbcore.contrib.directory.factories.entries.CompanyFactory")

    @factory.post_generation
    def create_initial_portfolio(product_group, *args, **kwargs):
        if product_group.id and not product_group.portfolios.exists():
            portfolio = PortfolioFactory.create()
            InstrumentPortfolioThroughModel.objects.create(instrument=product_group, portfolio=portfolio)


class ProductGroupRepresentantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductGroupRepresentant

    product_group = factory.SubFactory(ProductGroupFactory)
    representant = factory.SubFactory("wbcore.contrib.directory.factories.entries.CompanyFactory")
    country = factory.SubFactory("wbcore.contrib.geography.factories.CountryFactory")
