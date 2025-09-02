from datetime import date

import pytest
from django.contrib.auth.models import Permission
from django.db import models
from django.test.client import RequestFactory
from faker import Faker
from psycopg.types.range import DateRange
from rest_framework.reverse import reverse
from rest_framework.test import force_authenticate
from wbfdm.models import InstrumentPrice

from wbportfolio.models import InstrumentPortfolioThroughModel, Product
from wbportfolio.viewsets import ProductModelViewSet

fake = Faker()


@pytest.mark.django_db
class TestProductModelViewSet:
    def create_queryset(self, portfolio_factory, product_factory, instrument_price_factory, customer_trade_factory):
        for portfolio, product in zip(
            portfolio_factory.create_batch(4, invested_timespan=DateRange(date.min, date.max))
            + portfolio_factory.create_batch(2, invested_timespan=DateRange(date.min, date.max)),
            product_factory.create_batch(6),
        ):
            InstrumentPortfolioThroughModel.objects.update_or_create(
                instrument=product, defaults={"portfolio": portfolio}
            )
            prices = instrument_price_factory.create_batch(10, instrument=product, calculated=False)
            for price in prices:
                trade = customer_trade_factory.create(
                    transaction_date=price.date, underlying_instrument=product, portfolio=product.primary_portfolio
                )
                price.outstanding_shares = trade.shares
                price.save()

    def test_list(self, superuser):
        url = reverse("wbportfolio:product-list")
        request = RequestFactory().get(url)
        force_authenticate(request, user=superuser)
        view = ProductModelViewSet.as_view({"get": "list"})
        response = view(request)
        assert response.status_code == 200

    def test_get_aggregates(
        self, superuser, portfolio_factory, product_factory, instrument_price_factory, customer_trade_factory
    ):
        url = reverse("wbportfolio:product-list")
        self.create_queryset(portfolio_factory, product_factory, instrument_price_factory, customer_trade_factory)

        request = RequestFactory().get(f'{url}?price_date={InstrumentPrice.objects.latest("date").date}')
        request.user = superuser
        force_authenticate(request, user=superuser)

        view = ProductModelViewSet(request=request)
        view.request = request
        queryset = view.get_queryset()
        agg = view.get_aggregates(queryset, queryset)
        aum = float(
            queryset.filter(is_invested=True).aggregate(s=models.Sum("assets_under_management_usd"))["s"] or 0.0
        )
        assert float(list(agg["assets_under_management_usd"].values())[0]) == pytest.approx(aum, rel=1e-4)

    def test_queryset_superuser(self, superuser, product_factory):
        url = reverse("wbportfolio:product-list")
        request = RequestFactory().get(url)
        force_authenticate(request, user=superuser)
        view = ProductModelViewSet.as_view({"get": "list"})
        product_factory.create_batch(5)
        response = view(request)
        assert response.status_code == 200
        ids = [r["id"] for r in response.data["results"]]
        assert set(ids) == set(list(Product.objects.values_list("id", flat=True)))

    def test_queryset_normaluser(self, user, product_factory, person_factory):
        url = reverse("wbportfolio:product-list")
        request = RequestFactory().get(url)
        permission = Permission.objects.get(codename="view_product", content_type__app_label="wbportfolio")
        user.user_permissions.add(permission)
        force_authenticate(request, user=user)
        view = ProductModelViewSet.as_view({"get": "list"})
        public_product = product_factory.create()
        white_label_product = product_factory.create()
        white_label_product.white_label_customers.add(user.profile)

        other_client_product = product_factory.create()
        other_client_product.white_label_customers.add(person_factory.create())

        response = view(request)
        assert response.status_code == 200
        ids = [r["id"] for r in response.data["results"]]
        assert set(ids) == set([public_product.id, white_label_product.id])
