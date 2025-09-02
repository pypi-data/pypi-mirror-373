from decimal import Decimal

import factory
from faker import Faker
from wbfdm.factories import InstrumentPriceFactory

from wbportfolio.models import Order

fake = Faker()


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    order_proposal = factory.SubFactory("wbportfolio.factories.OrderProposalFactory")
    currency_fx_rate = Decimal(1.0)
    fees = Decimal(0.0)
    underlying_instrument = factory.SubFactory("wbfdm.factories.InstrumentFactory")
    shares = factory.Faker("pydecimal", min_value=10, max_value=1000, right_digits=4)

    @factory.post_generation
    def create_price(self, create, extracted, **kwargs):
        if create:
            p = InstrumentPriceFactory.create(
                instrument=self.underlying_instrument, date=self.value_date, calculated=False
            )
            self.price = p.net_value
            self.save()
