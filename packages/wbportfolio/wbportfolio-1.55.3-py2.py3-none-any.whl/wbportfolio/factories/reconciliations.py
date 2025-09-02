import factory

from wbportfolio.models import AccountReconciliation, AccountReconciliationLine


class AccountReconciliationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccountReconciliation

    account = factory.SubFactory("wbcrm.factories.AccountFactory")
    creator = factory.SubFactory("wbcore.contrib.authentication.factories.UserFactory")
    reconciliation_date = factory.Faker("date_this_year")


class AccountReconciliationLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccountReconciliationLine

    reconciliation = factory.SubFactory(AccountReconciliationFactory)
    product = factory.SubFactory("wbportfolio.factories.ProductFactory")
    price = factory.Faker("pydecimal", left_digits=4, right_digits=2)
    price_date = factory.Faker("date_this_year")
    shares = factory.Faker("pyint")
    shares_external = factory.Faker("pyint")
