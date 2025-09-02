from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.conf import settings
from dynamic_preferences.registries import global_preferences_registry
from faker import Faker
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.directory.factories import CompanyFactory, CustomerStatusFactory
from wbcore.contrib.directory.models import Company

from wbportfolio.contrib.company_portfolio.models import (
    CompanyPortfolioData,
    get_client_customer_status,
    get_lost_client_customer_status,
    get_returning_client_customer_status,
    get_tpm_customer_status,
)

fake = Faker()


def custom_get_potential(company_portfolio_data, val_date: date):
    return val_date


def custom_get_tiering(company_portfolio_data, aum: Decimal):
    return aum


@pytest.mark.django_db
class TestCompanyPortfolioDataUpdater:
    @pytest.fixture
    def company_portfolio_data(self):
        company = CompanyFactory.create()
        usd = Currency.objects.get_or_create(key="USD")[0]
        global_preferences = global_preferences_registry.manager()
        global_preferences["wbportfolio__tpm_customer_status"] = CustomerStatusFactory.create(title="TPM")
        global_preferences["wbportfolio__client_customer_status"] = CustomerStatusFactory.create(title="Client")
        return CompanyPortfolioData.objects.get_or_create(
            company=company, defaults={"potential_currency": usd, "assets_under_management_currency": usd}
        )[0]

    def test_get_assets_under_management_usd(self, company_portfolio_data, claim):
        claim.account.owner = company_portfolio_data.company
        claim.account.save()
        claim.status = "APPROVED"
        claim.save()
        assert company_portfolio_data.get_assets_under_management_usd(claim.date - timedelta(days=1)) == Decimal(0)
        assert (
            company_portfolio_data.get_assets_under_management_usd(claim.date)
            == claim.shares * claim.product.valuations.get(date=claim.date).net_value
        )

    def test__get_default_potential(
        self, company_portfolio_data, weekday, currency_fx_rates_factory, asset_allocation_factory
    ):
        currency_fx_rates_factory.create(
            currency=company_portfolio_data.assets_under_management_currency, date=weekday, value=Decimal(1)
        )

        initial_aum = Decimal(1000)
        invested_aum = Decimal(100)
        company_portfolio_data.assets_under_management = initial_aum
        company_portfolio_data.invested_assets_under_management_usd = invested_aum

        asset_allocation_1 = asset_allocation_factory.create(
            company=company_portfolio_data.company, percent=Decimal(0.8), max_investment=Decimal(0.2)
        )
        asset_allocation_2 = asset_allocation_factory.create(
            company=company_portfolio_data.company, percent=Decimal(0.2), max_investment=Decimal(0.3)
        )
        asset_allocation_1.refresh_from_db()
        asset_allocation_2.refresh_from_db()
        assert (
            company_portfolio_data._get_default_potential(weekday)
            == initial_aum * asset_allocation_1.percent * asset_allocation_1.max_investment
            + initial_aum * asset_allocation_2.percent * asset_allocation_2.max_investment
            - invested_aum
        )

    def test__get_default_tiering_for_client(self, company_portfolio_data):
        company_portfolio_data.company.customer_status = get_client_customer_status()
        company_portfolio_data.company.save()

        company_portfolio_data.invested_assets_under_management_usd = fake.pydecimal(
            min_value=10, max_value=100
        ) / Decimal(100)
        assert company_portfolio_data._get_default_tiering(Decimal(1)) == Company.Tiering.ONE

        company_portfolio_data.invested_assets_under_management_usd = fake.pydecimal(
            min_value=5, max_value=10
        ) / Decimal(100)
        assert company_portfolio_data._get_default_tiering(Decimal(1)) == Company.Tiering.TWO

        company_portfolio_data.invested_assets_under_management_usd = fake.pydecimal(
            min_value=2, max_value=5
        ) / Decimal(100)
        assert company_portfolio_data._get_default_tiering(Decimal(1)) == Company.Tiering.THREE

        company_portfolio_data.invested_assets_under_management_usd = fake.pydecimal(
            min_value=1, max_value=2
        ) / Decimal(100)
        assert company_portfolio_data._get_default_tiering(Decimal(1)) == Company.Tiering.FOUR

        company_portfolio_data.invested_assets_under_management_usd = fake.pydecimal(max_value=1) / Decimal(100)
        assert company_portfolio_data._get_default_tiering(Decimal(1)) == Company.Tiering.FIVE

    def test_get_customer_status(self, company_portfolio_data):
        # without AUM, the method should return the company customer status
        assert company_portfolio_data.get_customer_status() == company_portfolio_data.company.customer_status

        # add unvalid AUM
        company_portfolio_data.invested_assets_under_management_usd = -10
        assert (
            company_portfolio_data.get_customer_status() == company_portfolio_data.company.customer_status
        )  # unvalid aum will return as no aum

        # add positive AUM
        company_portfolio_data.invested_assets_under_management_usd = fake.pydecimal(positive=True)
        assert (
            company_portfolio_data.get_customer_status() == get_client_customer_status()
        )  # unvalid aum will return as no aum

        # ensure TPM are not considered as client even if they have AUM
        company_portfolio_data.company.customer_status = get_tpm_customer_status()
        company_portfolio_data.company.save()
        assert company_portfolio_data.get_customer_status() == get_tpm_customer_status()

    def test_get_lost_customer_status(self, company_portfolio_data):
        company_portfolio_data.company.customer_status = get_client_customer_status()
        company_portfolio_data.company.save()

        company_portfolio_data.invested_assets_under_management_usd = None
        assert company_portfolio_data.get_customer_status() == get_lost_client_customer_status()

    def test_returning_customer_status(self, company_portfolio_data):
        company_portfolio_data.company.customer_status = get_lost_client_customer_status()
        company_portfolio_data.company.save()

        company_portfolio_data.invested_assets_under_management_usd = fake.pydecimal(positive=True)
        assert company_portfolio_data.get_customer_status() == get_returning_client_customer_status()

    def test_staying_returning_customer_status(self, company_portfolio_data):
        company_portfolio_data.company.customer_status = get_returning_client_customer_status()
        company_portfolio_data.company.save()

        company_portfolio_data.invested_assets_under_management_usd = fake.pydecimal(positive=True)
        assert company_portfolio_data.get_customer_status() == get_returning_client_customer_status()

    def test_get_potential_from_custom_method(self, company_portfolio_data, weekday):
        settings.PORTFOLIO_COMPANY_DATA_POTENTIAL_METHOD = (
            "wbportfolio.contrib.company_portfolio.tests.test_models.custom_get_potential"
        )
        assert company_portfolio_data.get_potential(weekday) == weekday

    @pytest.mark.parametrize("total_aum", [fake.pydecimal()])
    def test_get_tiering_from_custom_method(self, company_portfolio_data, total_aum):
        settings.PORTFOLIO_COMPANY_DATA_TIERING_METHOD = (
            "wbportfolio.contrib.company_portfolio.tests.test_models.custom_get_potential"
        )
        assert company_portfolio_data.get_tiering(total_aum) == total_aum
