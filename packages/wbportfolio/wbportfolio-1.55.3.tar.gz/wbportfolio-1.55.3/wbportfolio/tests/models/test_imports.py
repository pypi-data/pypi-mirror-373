from decimal import Decimal

import pytest
from django.forms.models import model_to_dict
from faker import Faker
from pandas.tseries.offsets import BDay
from wbfdm.import_export.handlers.instrument_price import InstrumentPriceImportHandler
from wbfdm.models import InstrumentPrice

from wbportfolio.import_export.handlers.asset_position import AssetPositionImportHandler
from wbportfolio.import_export.handlers.fees import FeesImportHandler
from wbportfolio.import_export.handlers.trade import TradeImportHandler
from wbportfolio.models import AssetPosition, Fees, Trade

fake = Faker()


@pytest.mark.django_db
class TestImportMixinModel:
    def test_import_trade(self, import_source, product, portfolio, trade_factory):
        def serialize(trade):
            data = model_to_dict(trade)
            data["transaction_date"] = trade.transaction_date.strftime("%Y-%m-%d")
            data["value_date"] = trade.value_date.strftime("%Y-%m-%d")
            data["underlying_instrument"] = {"id": product.id}
            data["portfolio"] = portfolio.id
            data["currency"] = {"key": portfolio.currency.key}
            del data["id"]
            del data["import_source"]
            return data

        trade = trade_factory.build()
        data = {"data": [serialize(trade)]}

        # Import non existing data
        TradeImportHandler(import_source).process(data)
        assert Trade.objects.count() == 1

        # Import already existing data
        # import_source.data['data'][0]['shares'] *= 2

        TradeImportHandler(import_source).process(data)
        assert Trade.objects.count() == 1

    def test_import_price(self, import_source, product, instrument_price_factory, instrument):
        def serialize(val):
            data = model_to_dict(val)
            for k, v in data.items():
                if isinstance(v, Decimal):
                    data[k] = float(v)
            data["date"] = f"{val.date:%Y-%m-%d}"
            data["instrument"] = {"instrument_type": "product", "id": product.id}
            del data["id"]
            del data["import_source"]
            del data["currency_fx_rate_to_usd"]
            return data

        val = instrument_price_factory.build(instrument=instrument)
        data = {"data": [serialize(val)]}
        handler = InstrumentPriceImportHandler(import_source)
        # Import non existing data
        handler.process(data)
        assert InstrumentPrice.objects.count() == 1

        # Import already existing data
        data["data"][0]["net_value"] *= 2
        handler.process(data)
        assert InstrumentPrice.objects.count() == 1

    def test_import_fees(self, import_source, product_factory, portfolio, cash_factory, fees_factory):
        product = product_factory.create()
        portfolio = product.primary_portfolio
        cash_factory.create(currency=portfolio.currency)

        def serialize(fees):
            data = model_to_dict(fees)
            data["fee_date"] = fees.fee_date.strftime("%Y-%m-%d")
            data["product"] = product.id
            data["currency"] = {"key": portfolio.currency.key}
            del data["calculated"]
            del data["id"]
            del data["import_source"]
            return data

        fees = fees_factory.build(calculated=False)
        data = {"data": [serialize(fees)]}
        handler = FeesImportHandler(import_source)
        # Import non existing data
        handler.process(data)
        assert Fees.objects.count() == 1

        # Import already existing data
        data["data"][0]["total_value"] *= 2
        handler.process(data)
        assert Fees.objects.count() == 1

    def _serialize_position(self, pos, instrument, underlying):
        return {
            "date": f"{pos.date:%Y-%m-%d}",
            "initial_shares": pos.initial_shares,
            "initial_price": pos.initial_price,
            "weighting": pos.weighting,
            "initial_currency_fx_rate": Decimal(1),
            "asset_valuation_date": f"{pos.asset_valuation_date:%Y-%m-%d}",
            "currency": {"key": underlying.currency.key},
            "portfolio": {"id": instrument.id, "instrument_type": instrument.security_instrument_type.key},
            "underlying_instrument": {
                "instrument_type": underlying.instrument_type.key,
                "currency": {"key": underlying.currency.key},
                "ticker": underlying.ticker,
                "name": underlying.name,
                "exchange": {"bbg_composite": "US"},
            },
        }

    @pytest.mark.parametrize("val_date", [(fake.date_object())])
    def test_import_assetposition_product(
        self,
        val_date,
        import_source,
        product_factory,
        currency,
        equity_factory,
        index_factory,
        cash_factory,
        asset_position_factory,
    ):
        val_date = (val_date - BDay(0)).date()
        product_portfolio = product_factory.create()
        instruments = [
            equity_factory.create(currency=currency, instrument_type__name="Equity"),
            cash_factory.create(currency=currency, instrument_type__name="Cash"),
            product_factory.create(currency=currency, instrument_type__name="Product"),
            index_factory.create(currency=currency, instrument_type__name="Index"),
        ]
        data = {
            "data": [
                self._serialize_position(
                    asset_position_factory.build(
                        date=val_date, underlying_instrument=instrument, weighting=Decimal("0.25")
                    ),
                    product_portfolio,
                    instrument,
                )
                for instrument in instruments
            ]
        }
        handler = AssetPositionImportHandler(import_source)

        # Import non existing data
        handler.process(data)
        for instrument in instruments:
            # we check that the position was created
            a = AssetPosition.objects.get(
                underlying_instrument=instrument, date=val_date, portfolio=product_portfolio.portfolio
            )
            assert a
            if instrument.is_cash:
                assert InstrumentPrice.objects.get(instrument=instrument, date=val_date, calculated=False, net_value=1)
            else:
                # and as this is an import handle by the assetposition handler, we expect the underlying instrument price to be created from the position initial price
                assert InstrumentPrice.objects.get(
                    instrument=instrument, date=val_date, calculated=False, net_value=a.initial_price
                )

        # Import already existing data
        data["data"][0]["initial_price"] *= 2

        handler.process(data)
        assert AssetPosition.objects.count() == 4

    def test_import_assetposition_product_group(
        self, import_source, product_group, currency, equity, asset_position_factory
    ):
        positions = asset_position_factory.build(underlying_instrument=equity, weighting=Decimal("1"))
        data = {"data": [self._serialize_position(positions, product_group, equity)]}

        # Import non existing data
        handler = AssetPositionImportHandler(import_source)

        handler.process(data)
        assert AssetPosition.objects.count() == 1

    def test_import_assetposition_index(
        self, import_source, index, portfolio, currency, equity, asset_position_factory
    ):
        positions = asset_position_factory.build(underlying_instrument=equity, weighting=Decimal("1"))
        index.portfolios.add(portfolio)
        data = {"data": [self._serialize_position(positions, index, equity)]}

        # Import non existing data
        handler = AssetPositionImportHandler(import_source)

        handler.process(data)
        assert AssetPosition.objects.count() == 1
