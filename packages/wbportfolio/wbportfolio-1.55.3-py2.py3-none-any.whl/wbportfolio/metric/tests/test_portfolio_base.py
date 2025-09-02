from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from django.db.models import Sum
from faker import Faker
from wbfdm.dataloaders.proxies import InstrumentDataloaderProxy
from wbfdm.enums import Financial

from wbportfolio.factories import AssetPositionFactory, PortfolioFactory
from wbportfolio.models import AssetPosition

from ..backends.portfolio_base import DataLoader

fake = Faker()


@pytest.mark.django_db
class TestPortfolioBaseDataloader:
    @pytest.fixture
    def dataloader(self, weekday):
        portfolio = PortfolioFactory.create()
        AssetPositionFactory.create_batch(5, portfolio=portfolio, date=weekday, is_estimated=False)
        dataloader = DataLoader(portfolio, weekday)
        base_df = dataloader.base_df
        columns = dataloader.columns_map.keys()
        dataloader.__dict__["market_capitalization_df"] = pd.DataFrame(
            np.random.randint(1e6, 1e9, size=(base_df.shape[0], len(columns))), index=base_df.index, columns=columns
        )
        dataloader.__dict__["ebit_usd_df"] = pd.DataFrame(
            np.random.randint(100, 100000, size=(base_df.shape[0], len(columns))), index=base_df.index, columns=columns
        )
        dataloader.__dict__["total_assets_usd_df"] = pd.DataFrame(
            np.random.randint(1e6, 1e9, size=(base_df.shape[0], len(columns))), index=base_df.index, columns=columns
        )
        dataloader.__dict__["liabilities_usd_df"] = pd.DataFrame(
            np.random.randint(1e6, 1e9, size=(base_df.shape[0], len(columns))), index=base_df.index, columns=columns
        )
        return dataloader

    @patch.object(InstrumentDataloaderProxy, "financials")
    def test__get_financial_df(self, mock_fct, dataloader: DataLoader):
        return_value = []
        base_df = dataloader.base_df
        for pivot_date in dataloader.pivot_dates:
            for instrument_id in base_df.index:
                return_value.append({"instrument_id": instrument_id, "year": pivot_date.year, "value": fake.pyfloat()})
        mock_fct.return_value = return_value
        res = dataloader._get_financial_df(Financial.EBIT)
        pd.testing.assert_index_equal(res.index, base_df.index)
        assert set(res.columns.tolist()) == set(dataloader.columns_map.keys())

    @patch.object(InstrumentDataloaderProxy, "financials")
    def test__get_financial_df_empty(self, mock_fct, dataloader: DataLoader):
        mock_fct.return_value = []
        with pytest.raises(ValueError):
            dataloader._get_financial_df(Financial.EBIT)

    def test_base_df(self, dataloader):
        base_df = dataloader.base_df
        total_portfolio_weight = AssetPosition.objects.filter(
            portfolio=dataloader.portfolio, date=dataloader.val_date
        ).aggregate(c=Sum("weighting"))["c"]
        for instrument_id, df in base_df.to_dict("index").items():
            for key, value in df.items():
                pos = AssetPosition.objects.get(
                    portfolio=dataloader.portfolio, date=dataloader.val_date, underlying_instrument=instrument_id
                )
                if key == "weighting":
                    assert float(getattr(pos, key) / total_portfolio_weight) == pytest.approx(value, abs=1e-6)
                else:
                    assert float(getattr(pos, key)) == value

    # Test portfolio metric computation
    def test_portfolio_ownership_df(self, dataloader):
        assert dataloader.portfolio_ownership_df.dropna().empty is False
        pd.testing.assert_frame_equal(
            dataloader.portfolio_ownership_df,
            (1.0 / dataloader.market_capitalization_df).multiply(dataloader.base_df.total_value_fx_usd, axis=0),
            check_exact=True,
        )

    def test_portfolio_ebit_usd_df(self, dataloader):
        assert dataloader.portfolio_ebit_usd_df.dropna().empty is False
        pd.testing.assert_frame_equal(
            dataloader.portfolio_ebit_usd_df,
            dataloader.portfolio_ownership_df * dataloader.ebit_usd_df,
            check_exact=True,
        )
        pd.testing.assert_series_equal(
            dataloader.portfolio_ebit_usd_df.aggregate, dataloader.portfolio_ebit_usd_df.sum(axis=0), check_exact=True
        )

    def test_portfolio_total_assets_usd_df(self, dataloader):
        assert dataloader.portfolio_total_assets_usd_df.dropna().empty is False
        pd.testing.assert_frame_equal(
            dataloader.portfolio_total_assets_usd_df,
            dataloader.portfolio_ownership_df * dataloader.total_assets_usd_df,
            check_exact=True,
        )
        pd.testing.assert_series_equal(
            dataloader.portfolio_total_assets_usd_df.aggregate,
            dataloader.portfolio_total_assets_usd_df.sum(axis=0),
            check_exact=True,
        )

    def test_portfolio_liabilities_usd_df(self, dataloader):
        assert dataloader.portfolio_liabilities_usd_df.dropna().empty is False
        pd.testing.assert_frame_equal(
            dataloader.portfolio_liabilities_usd_df,
            dataloader.portfolio_ownership_df * dataloader.liabilities_usd_df,
            check_exact=True,
        )
        pd.testing.assert_series_equal(
            dataloader.portfolio_liabilities_usd_df.aggregate,
            dataloader.portfolio_liabilities_usd_df.sum(axis=0),
            check_exact=True,
        )

    def test_portfolio_aggregation_capital_employed(self, dataloader):
        assert dataloader.portfolio_aggregation_capital_employed.dropna().empty is False
        pd.testing.assert_series_equal(
            dataloader.portfolio_aggregation_capital_employed,
            dataloader.portfolio_total_assets_usd_df.aggregate - dataloader.portfolio_liabilities_usd_df.aggregate,
            check_exact=True,
        )

    def test_portfolio_aggregation_roce(self, dataloader):
        assert dataloader.portfolio_aggregation_roce.dropna().empty is False
        pd.testing.assert_series_equal(
            dataloader.portfolio_aggregation_roce,
            dataloader.portfolio_ebit_usd_df.aggregate
            / dataloader.portfolio_aggregation_capital_employed.rolling(2).mean(),
            check_exact=True,
        )
