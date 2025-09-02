import factory

from wbportfolio.models import PortfolioRole


class ProductPortfolioRoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PortfolioRole

    role_type = factory.Iterator([PortfolioRole.RoleType.PORTFOLIO_MANAGER, PortfolioRole.RoleType.ANALYST])
    person = factory.SubFactory("wbcore.contrib.authentication.factories.users.AuthenticatedPersonFactory")
    instrument = factory.SubFactory("wbportfolio.factories.ProductFactory")
    weighting = factory.Faker("pyfloat", min_value=0.1, max_value=1)


class ManagerPortfolioRoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PortfolioRole

    role_type = factory.Iterator([PortfolioRole.RoleType.RISK_MANAGER, PortfolioRole.RoleType.MANAGER])
    person = factory.SubFactory("wbcore.contrib.directory.factories.entries.PersonFactory")
