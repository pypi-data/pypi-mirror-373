import pytest
from faker import Faker
from pandas.tseries.offsets import BDay
from rest_framework.test import APIRequestFactory

from wbportfolio.viewsets.positions import AggregatedAssetPositionLiquidityPandasView

fake = Faker()


@pytest.mark.django_db
class TestPandasViewSet:
    def test_get_dataframe(self, instrument_price_factory, asset_position_factory, equity, portfolio, weekday):
        request = APIRequestFactory().get("")
        request.query_params = dict()
        # Make instances of AP, instrument prices.
        i1 = instrument_price_factory.create(
            instrument=equity,
            date=weekday,
            volume_50d=1000,
            net_value=10,
            instrument__currency__key="USD",
        )
        i2 = instrument_price_factory.create(
            instrument=equity,
            date=(i1.date - BDay(1)).date(),
            volume_50d=1100,
            net_value=11,
            instrument__currency__key="USD",
        )
        a1 = asset_position_factory.create(
            portfolio=portfolio,
            portfolio__currency__key="USD",
            underlying_instrument=i1.instrument,
            date=i1.date,
            initial_shares=1000,
        )
        a2 = asset_position_factory.create(
            portfolio=portfolio,
            portfolio__currency__key="USD",
            underlying_instrument=i1.instrument,
            date=i2.date,
            initial_shares=1000,
        )

        # Make an empty df
        request.GET = request.GET.copy()
        request.GET.update(
            {
                "historic_date": (i1.date - BDay(2)).date().strftime("%Y-%m-%d"),
                "compared_date": (i1.date - BDay(3)).date().strftime("%Y-%m-%d"),
                "bigger_than_x": 1,
            }
        )
        df_empty = AggregatedAssetPositionLiquidityPandasView(request=request)._get_dataframe()

        # Run the function with existing second_date in asset_position
        request.GET["compared_date"] = i2.date.strftime("%Y-%m-%d")

        # Run with 2 existing dates.
        request.GET["historic_date"] = i1.date.strftime("%Y-%m-%d")
        df = AggregatedAssetPositionLiquidityPandasView(request=request)._get_dataframe()
        # Coverage:
        assert df_empty.empty  # df is empty
        # Unit tests:
        s_i1 = df.set_index("id").loc[i1.instrument.id]
        assert s_i1.at["liquidity_first_date"] == round(a1.initial_shares / (i1.volume_50d * 0.33), 2)
        assert s_i1.at["liquidity_second_date"] == round(a2.initial_shares / (i2.volume_50d * 0.33), 2)
