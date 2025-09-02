import factory

from wbportfolio.models import Custodian


class CustodianFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("company")
    mapping = factory.List([factory.Faker("company") for _ in range(5)])

    class Meta:
        model = Custodian
        django_get_or_create = ("name",)
