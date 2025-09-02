import pytest
from faker import Faker
from pandas.tseries.offsets import BDay
from wbfdm.factories import InstrumentFactory
from wbfdm.models import InstrumentPrice

from wbportfolio.models import (
    Adjustment,
    PortfolioInstrumentPreferredClassificationThroughModel,
)

fake = Faker()


@pytest.mark.django_db
class TestMergeInstrument:
    @pytest.fixture()
    def merged_instrument(self):
        return InstrumentFactory.create()

    @pytest.fixture()
    def main_instrument(self):
        return InstrumentFactory.create()

    def test_assets(
        self, main_instrument, merged_instrument, asset_position_factory, instrument_price_factory, weekday
    ):
        """
        Test if the asset positions attached to the merged instrument are forwarded to the main instrument as well as the underlying instrument price
        """
        p1 = instrument_price_factory.create(instrument=main_instrument, calculated=False, date=weekday)
        p2 = instrument_price_factory.create(instrument=merged_instrument, calculated=False, date=weekday)

        a1 = asset_position_factory.create(underlying_instrument=main_instrument, date=weekday)
        a2 = asset_position_factory.create(underlying_instrument=merged_instrument, date=weekday)

        assert a1.underlying_quote_price == p1
        assert a2.underlying_quote_price == p2
        main_instrument.merge(merged_instrument)
        a2.refresh_from_db()
        a1.refresh_from_db()

        assert a1.underlying_instrument == main_instrument  # Make sure this doesn't change
        assert a1.underlying_quote_price == p1  # Make sure this doesn't change
        assert a2.underlying_instrument == main_instrument
        assert a2.underlying_quote_price == p1

    def test_roles(self, main_instrument, merged_instrument, product_portfolio_role_factory):
        """
        Test if the role attached to the merged instrument are forwarded to the main instrument
        """
        role = product_portfolio_role_factory.create(instrument=merged_instrument)
        main_instrument.merge(merged_instrument)
        role.refresh_from_db()
        assert role.instrument == main_instrument

    def test_classifications(self, main_instrument, merged_instrument, portfolio_factory, classification_factory):
        """
        Test if preferred classification are forwarded to the main instrument
        """
        main_portfolio = portfolio_factory.create()
        merged_portfolio = portfolio_factory.create()

        PortfolioInstrumentPreferredClassificationThroughModel.objects.create(
            instrument=main_instrument, portfolio=main_portfolio, classification=classification_factory.create()
        )
        PortfolioInstrumentPreferredClassificationThroughModel.objects.create(
            instrument=merged_instrument, portfolio=merged_portfolio, classification=classification_factory.create()
        )
        main_instrument.merge(merged_instrument)

        assert set(main_instrument.preferred_portfolio_classifications.all()) == set(
            [main_portfolio, merged_portfolio]
        )

    def test_transactions(self, main_instrument, merged_instrument, trade_factory):
        """
        Test if the attached transactions to the merged instrument are forwarded to the main instrument
        """
        merged_t = trade_factory.create(underlying_instrument=merged_instrument)
        main_t = trade_factory.create(underlying_instrument=main_instrument)

        main_instrument.merge(merged_instrument)
        merged_t.refresh_from_db()
        main_t.refresh_from_db()

        merged_t.underlying_instrument = main_instrument
        main_t.underlying_instrument = main_instrument  # make sure this does not change

    def test_instrument_prices(self, main_instrument, merged_instrument, instrument_price_factory, weekday):
        """
        Test if the attached prices to the merged instrument are forwarded to the main instrument but does not overlaps them (if price already exists, the overlapping merged price are simply deleted)
        """
        main_p1 = instrument_price_factory.create(instrument=main_instrument, calculated=False, date=weekday)

        merged_p1 = instrument_price_factory.create(instrument=merged_instrument, calculated=False, date=weekday)
        merged_p2 = instrument_price_factory.create(
            instrument=merged_instrument, calculated=False, date=weekday + BDay(1)
        )

        assert main_instrument.valuations.count() == 1
        main_instrument.merge(merged_instrument)

        assert (
            main_instrument.valuations.get(date=weekday).net_value == main_p1.net_value
        )  # Check that the existing price was not overlaps by the merged instrument price at that day
        assert (
            main_instrument.valuations.get(date=weekday + BDay(1)).net_value == merged_p2.net_value
        )  # Check that the price not existing from merged instrument was appended to the main instrument serie
        with pytest.raises(InstrumentPrice.DoesNotExist):
            merged_p1.refresh_from_db()

    def test_adjustments(self, main_instrument, merged_instrument, adjustment_factory, weekday):
        """
        Test if the attached adjustments to the merged instrument are forwarded to the main instrument but does not overlaps them (if split already exists, the overlapping merged split are simply deleted)
        """
        main_s1 = adjustment_factory.create(instrument=main_instrument, date=weekday)

        merged_s1 = adjustment_factory.create(instrument=merged_instrument, date=weekday)
        merged_s2 = adjustment_factory.create(instrument=merged_instrument, date=weekday + BDay(1))
        merged_s2.refresh_from_db()  # We refresh from db to cast the decimal factor to its proper number of decimal places (kind of stupid but..)
        main_s1.refresh_from_db()

        assert main_instrument.pms_adjustments.count() == 1
        main_instrument.merge(merged_instrument)

        assert (
            main_instrument.pms_adjustments.get(date=weekday).factor == main_s1.factor
        )  # Check that the existing split was not overlaps by the merged instrument split at that day
        assert (
            main_instrument.pms_adjustments.get(date=weekday + BDay(1)).factor == merged_s2.factor
        )  # Check that the split not existing from merged instrument was appended to the main instrument serie
        with pytest.raises(Adjustment.DoesNotExist):
            merged_s1.refresh_from_db()
