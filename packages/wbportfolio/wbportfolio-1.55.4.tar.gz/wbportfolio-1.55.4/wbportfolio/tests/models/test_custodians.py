import pytest


@pytest.mark.django_db
class TestCustodianModel:
    def test_init(self, custodian_factory):
        custodian = custodian_factory.create()
        assert custodian.id is not None

    def test_str(self, custodian_factory):
        custodian = custodian_factory.create()
        assert str(custodian) == f"{custodian.name}"
