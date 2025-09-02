import random

import factory
from faker import Faker

from wbportfolio.models import Fees

faker = Faker()


class FeesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Fees

    currency_fx_rate = 1.0
    fee_date = factory.Faker("date_object")
    total_value = factory.LazyAttribute(lambda o: random.randint(1, 1000))
    transaction_subtype = factory.Faker("random_element", elements=[x[0] for x in Fees.Type.choices])
    product = factory.SubFactory("wbportfolio.factories.products.ProductFactory")
    currency = factory.SubFactory("wbcore.contrib.currency.factories.CurrencyFactory")
