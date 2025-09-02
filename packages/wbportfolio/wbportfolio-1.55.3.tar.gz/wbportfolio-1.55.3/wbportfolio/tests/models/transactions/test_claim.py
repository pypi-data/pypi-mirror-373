import random
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from faker import Faker

from wbportfolio.models import Claim, Trade

fake = Faker()


@pytest.mark.django_db
class TestClaimModel:
    def test_init(self, claim):
        assert claim.id is not None

    def test_filter_claims_for_user(self, user, claim_factory, account_factory, account_role_factory):
        from wbcore.permissions.registry import user_registry

        no_account_claims = claim_factory.create(account=None)
        private_claim = claim_factory.create(account=account_factory.create(is_public=False))
        public_claim = claim_factory.create(account=account_role_factory.create(entry=user.profile.entry_ptr).account)
        # if normal user, can only see its own claim, with an attached account
        assert set(Claim.objects.filter_for_user(user)) == {public_claim}
        user.user_permissions.add(
            Permission.objects.get(content_type__app_label="authentication", codename="is_internal_user")
        )
        user_registry.reset_cache()
        user = get_user_model().objects.get(
            id=user.id
        )  # we refetch user to clear perm cache, doesn't happen with refresh_from_db
        # if insternal user, they can also see claim without account
        assert set(Claim.objects.filter_for_user(user)) == {no_account_claims, public_claim}
        user.user_permissions.add(
            Permission.objects.get(content_type__app_label="wbcrm", codename="administrate_account")
        )
        user = get_user_model().objects.get(
            id=user.id
        )  # we refetch user to clear perm cache, doesn't happen with refresh_from_db
        # administrator can see everything
        assert set(Claim.objects.filter_for_user(user)) == {no_account_claims, public_claim, private_claim}

    def test_account_merging(self, account_factory, claim):
        base_account = account_factory.create()
        merged_account = claim.account
        assert base_account.reference_id != merged_account.reference_id
        base_account.merge(merged_account)
        claim.refresh_from_db()
        assert claim.account == base_account
        assert claim.reference == str(merged_account.reference_id)

    @pytest.mark.parametrize(
        "shares,unvalid_status",
        [
            (
                Decimal(50),
                random.choice(
                    [Claim.Status.WITHDRAWN, Claim.Status.AUTO_MATCHED, Claim.Status.PENDING, Claim.Status.APPROVED]
                ),
            )
        ],
    )
    def test_auto_match_on_claim_save(
        self, weekday, shares, unvalid_status, product, claim_factory, customer_trade_factory
    ):
        valid_trade = customer_trade_factory.create(
            underlying_instrument=product,
            portfolio=product.primary_portfolio,
            transaction_date=fake.date_between(
                weekday - timedelta(days=Trade.TRADE_WINDOW_INTERVAL),
                weekday + timedelta(days=Trade.TRADE_WINDOW_INTERVAL),
            ),
            shares=fake.pydecimal(min_value=int(shares - 1), max_value=int(shares + 1)),
        )
        claim = claim_factory.create(product=product, date=weekday, shares=shares, trade=None, status=unvalid_status)
        assert claim.status == unvalid_status
        assert claim.trade is None

        claim = claim_factory.create(
            product=product, date=weekday, shares=shares, trade=None, status=Claim.Status.DRAFT
        )
        assert claim.status == Claim.Status.AUTO_MATCHED
        assert claim.trade == valid_trade

    @pytest.mark.parametrize(
        "shares,unvalid_status",
        [
            (
                Decimal(50),
                random.choice(
                    [Claim.Status.WITHDRAWN, Claim.Status.AUTO_MATCHED, Claim.Status.PENDING, Claim.Status.APPROVED]
                ),
            )
        ],
    )
    def test_claim_auto_match_on_trade_creation(
        self, weekday, shares, unvalid_status, product, claim_factory, customer_trade_factory
    ):
        claim = claim_factory.create(product=product, date=weekday, shares=shares, trade=None, status=unvalid_status)
        trade = customer_trade_factory.create(
            underlying_instrument=product,
            portfolio=product.primary_portfolio,
            transaction_date=fake.date_between(
                weekday - timedelta(days=Trade.TRADE_WINDOW_INTERVAL),
                weekday + timedelta(days=Trade.TRADE_WINDOW_INTERVAL),
            ),
            shares=fake.pydecimal(min_value=int(shares - 1), max_value=int(shares + 1)),
        )
        assert claim.status == unvalid_status
        assert claim.trade is None

        # we delete the trade and set the claim status to draft, where we expect a newly created trade to be automatch
        trade.delete()
        claim.status = Claim.Status.DRAFT
        claim.save()
        trade = customer_trade_factory.create(
            underlying_instrument=product,
            portfolio=product.primary_portfolio,
            transaction_date=fake.date_between(
                weekday - timedelta(days=Trade.TRADE_WINDOW_INTERVAL),
                weekday + timedelta(days=Trade.TRADE_WINDOW_INTERVAL),
            ),
            shares=fake.pydecimal(min_value=int(shares - 1), max_value=int(shares + 1)),
        )
        claim.refresh_from_db()
        assert claim.status == Claim.Status.AUTO_MATCHED
        assert claim.trade == trade
