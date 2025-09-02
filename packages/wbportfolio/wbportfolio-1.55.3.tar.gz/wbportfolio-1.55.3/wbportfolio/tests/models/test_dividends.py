import pytest


@pytest.mark.django_db
class TestDividendModel:
    def test_init(self, dividend_transaction):
        assert dividend_transaction.id is not None
