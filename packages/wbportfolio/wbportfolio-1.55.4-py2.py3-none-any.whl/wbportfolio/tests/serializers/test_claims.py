import pytest

from wbportfolio.serializers import ClaimModelSerializer


@pytest.mark.django_db
class TestClaimModelSerializer:
    def test_serialize(self, claim):
        claim.trade_type = True
        claim.quantity = 1000
        serializer = ClaimModelSerializer(claim)
        assert serializer.data

    def test_validate(self):
        data = {
            "trade_type": True,
            "quantity": 1000,
            "as_shares": True,
            "date": "2024-01-01",
        }
        serializer = ClaimModelSerializer(data=data)
        assert serializer.is_valid()
