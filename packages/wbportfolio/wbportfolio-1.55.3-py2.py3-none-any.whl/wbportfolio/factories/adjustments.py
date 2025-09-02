import factory
from faker import Faker
from pandas.tseries.offsets import BDay

from wbportfolio.models import Adjustment

fake = Faker()


class AdjustmentFactory(factory.django.DjangoModelFactory):
    date = factory.LazyAttribute(lambda o: (fake.future_date() + BDay(0)).date())
    instrument = factory.SubFactory("wbfdm.factories.instruments.InstrumentFactory")
    factor = factory.Faker("pydecimal", min_value=2, max_value=10)
    last_handler = factory.SubFactory("wbcore.contrib.directory.factories.entries.PersonFactory")
    status = Adjustment.Status.PENDING

    class Meta:
        model = Adjustment
