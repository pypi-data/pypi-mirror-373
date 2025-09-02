import factory
from pandas.tseries.offsets import BDay
from wbfdm.factories.instrument_prices import InstrumentPriceFactory

from wbportfolio.models.transactions.claim import Claim


class ClaimFactory(factory.django.DjangoModelFactory):
    status = Claim.Status.DRAFT
    account = factory.SubFactory("wbcrm.factories.AccountFactory")
    trade = factory.SubFactory("wbportfolio.factories.CustomerTradeFactory")
    product = factory.LazyAttribute(lambda x: x.trade.product)
    claimant = factory.SubFactory("wbcore.contrib.directory.factories.entries.PersonFactory")
    creator = factory.SubFactory("wbcore.contrib.directory.factories.entries.PersonFactory")
    date = factory.LazyAttribute(lambda x: (x.trade.transaction_date - BDay(0)).date())
    bank = factory.Faker("company")
    reference = factory.Faker("company")
    shares = factory.LazyAttribute(lambda x: x.trade.shares)
    nominal_amount = factory.LazyAttribute(lambda x: x.shares * x.product.share_price)
    external_id = factory.Sequence(lambda n: f"{n:06}")

    @factory.post_generation
    def create_product_val(self, create, extracted, **kwargs):
        if extracted is None or extracted is True:
            InstrumentPriceFactory.create(instrument=self.product, date=self.date, calculated=False)

    class Meta:
        model = Claim


class PositiveClaimFactory(ClaimFactory):
    shares = factory.Faker("pydecimal", min_value=0, max_value=1000000)


class NegativeClaimFactory(ClaimFactory):
    shares = factory.Faker("pydecimal", min_value=-1000000, max_value=0)


class ApprovedClaimFactory(ClaimFactory):
    status = Claim.Status.APPROVED
