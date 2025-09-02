import random
from datetime import timedelta

import pytest
from django.db.models import ProtectedError
from faker import Faker

from wbportfolio.models import Trade
from wbportfolio.models.transactions.claim import Claim

fake = Faker()


@pytest.mark.django_db
class TestCustomerTradeModel:
    def test_delete_without_claims(self, trade):
        """
        Simple test to check if a trade without claim is properly deleted
        """
        trade.delete()
        with pytest.raises(Trade.DoesNotExist):
            trade.refresh_from_db()

    @pytest.mark.parametrize("claim_status", Claim.Status.names)
    def test_delete_trade_with_claim(self, customer_trade_factory, claim_factory, claim_status):
        """
        Simple test to check if a trade with claim a valid claim (Pending or Approved9 can't be deleted but
        a trade with a draft, withdrawn or auto approved claim can.
        """
        customer_trade = customer_trade_factory.create()
        claim = claim_factory.create(trade=customer_trade, status=claim_status)

        # If claim is among the non approved type, we expect the deletion to succeed and the claim to be unlinked
        if claim.status in [Claim.Status.DRAFT, Claim.Status.AUTO_MATCHED, Claim.Status.WITHDRAWN]:
            customer_trade.delete()
            claim.refresh_from_db()
            assert not claim.trade
            with pytest.raises(Trade.DoesNotExist):
                customer_trade.refresh_from_db()
        else:
            # If the claim is approved or pending, and in absence of any other similar trades to reassign the claim to, we expect the deletion to failed
            with pytest.raises(ProtectedError):
                customer_trade.delete()

    def test_delete_trade_with_approved_claims_but_similar_trades_summing_0(
        self, customer_trade_factory, claim_factory
    ):
        """
        A test to check that even trade with approved claims attach can be deleted if the sum of the shares of the similar trades the same date equals to 0
        """
        trade1 = customer_trade_factory.create()
        claim1 = claim_factory.create(trade=trade1, status=Claim.Status.APPROVED)
        trade1.marked_for_deletion = True
        trade1.save()

        # Claims is attached, no other similar trade is present, we don't expect the deletion to be possible
        with pytest.raises(ProtectedError):
            trade1.delete()

        # We create a negative trade that will annihilate trade1
        trade2 = customer_trade_factory.create(
            underlying_instrument=trade1.underlying_instrument,
            portfolio=trade1.portfolio,
            transaction_date=trade1.transaction_date,
            shares=-trade1.shares,
        )
        # That we claim
        claim2 = claim_factory.create(trade=trade2, status=Claim.Status.APPROVED)
        trade2.marked_for_deletion = True
        trade2.save()

        # Now, sum of all trades linked to this product at that date sums to 0, we can destroy all trades and unliked the associated claims
        trade1.delete()
        claim1.refresh_from_db()
        claim2.refresh_from_db()
        assert not claim1.trade
        assert claim1.status == Claim.Status.DRAFT
        assert not claim2.trade
        assert claim2.status == Claim.Status.DRAFT

        # trade2 is unclaimed and can be safely deleted
        trade2.delete()
        with pytest.raises(Trade.DoesNotExist):
            trade2.refresh_from_db()

    @pytest.mark.parametrize(
        "allowed_timedeltda", [random.randint(-Trade.TRADE_WINDOW_INTERVAL, Trade.TRADE_WINDOW_INTERVAL)]
    )
    def test_trade_delete_shift_claims(self, customer_trade_factory, claim_factory, allowed_timedeltda):
        """
        Test main functionality: when a trade is linked to an approved claim and is marked for deletion, we try to find the closest trade non marked for deletion or pending and unclaimed.

        If this succeed, the claim is forwarded to this other trade. Otherwise, it will fail.
        """
        trade1 = customer_trade_factory.create()
        claim1 = claim_factory.create(trade=trade1, status=Claim.Status.APPROVED)
        trade1.marked_for_deletion = True
        trade1.save()

        # We expect the claim to be reassigned to this similar "non marked for deletion" trade
        similar_unclaimed_trade = customer_trade_factory.create(
            marked_for_deletion=False,
            pending=False,
            underlying_instrument=trade1.underlying_instrument,
            portfolio=trade1.portfolio,
            transaction_subtype=trade1.transaction_subtype,
            transaction_date=trade1.transaction_date + timedelta(days=allowed_timedeltda),
            shares=trade1.shares,
        )
        trade1.delete()
        with pytest.raises(Trade.DoesNotExist):
            trade1.refresh_from_db()
        claim1.refresh_from_db()
        assert claim1.trade == similar_unclaimed_trade
