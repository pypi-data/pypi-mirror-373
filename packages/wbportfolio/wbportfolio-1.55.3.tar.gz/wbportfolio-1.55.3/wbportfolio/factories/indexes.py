import random

import factory
from faker import Faker
from wbfdm.factories import InstrumentFactory, InstrumentTypeFactory

from wbportfolio.models import Index

fake = Faker()


class IndexFactory(InstrumentFactory):
    risk_scale = factory.LazyAttribute(lambda o: random.randint(1, 7))

    instrument_type = factory.LazyAttribute(lambda o: InstrumentTypeFactory.create(name="Index", key="index"))

    class Meta:
        model = Index
