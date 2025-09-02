from datetime import timedelta

import pytest
from faker import Faker

from wbportfolio.factories import ProductFactory

fake = Faker()


class PortfolioTestMixin:
    @pytest.fixture
    def active_product(self, weekday):
        return ProductFactory.create(inception_date=weekday - timedelta(days=30), delisted_date=None)
