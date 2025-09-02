import pytest
from faker import Faker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory
from wbcore.contrib.authentication.factories.users import UserFactory
from wbcore.contrib.directory.factories import EntryFactory
from wbcore.contrib.directory.models import Entry
from wbcore.utils.strings import format_number
from wbcrm.factories.accounts import AccountFactory, AccountRoleFactory
from wbcrm.models import Account

from wbportfolio.factories.claim import ClaimFactory
from wbportfolio.models.transactions.claim import Claim
from wbportfolio.viewsets.transactions.claim import (
    ClaimAccountModelViewSet,
    ClaimAPIModelViewSet,
    ClaimEntryModelViewSet,
    ClaimModelViewSet,
    ClaimProductModelViewSet,
    ClaimRepresentationViewSet,
    ClaimTradeModelViewSet,
    ConsolidatedTradeSummaryDistributionChart,
    ConsolidatedTradeSummaryTableView,
    CumulativeNNMChartView,
    NegativeTermimalAccountPerProductModelViewSet,
    ProfitAndLossPandasView,
)

fake = Faker()


@pytest.mark.django_db
class TestClaimModelViewSet:
    def test_aggregate(self, claim):
        view = ClaimModelViewSet()
        queryset = Claim.objects.all()
        agg = view.get_aggregates(queryset, paginated_queryset=queryset)
        assert agg["shares"]["Σ"] == format_number(claim.shares, decimal=4)

    @pytest.fixture
    def account_user(self):
        # True, we create a superuser

        # if fake.pybool():
        #     user = UserFactory.create(is_superuser=True)
        # else:
        user = UserFactory.create(is_superuser=False)
        entry = Entry.objects.get(id=user.profile.id)

        # Create a bunch of account and roles
        public_account = AccountFactory.create(is_public=True, owner=EntryFactory.create())
        child_public_account = AccountFactory.create(parent=public_account, owner=EntryFactory.create())
        ClaimFactory.create(account=public_account)
        ClaimFactory.create(account=child_public_account)
        AccountRoleFactory.create(account=public_account, entry=entry)
        AccountRoleFactory.create(account=public_account)
        private_account = AccountFactory.create(is_public=False, owner=EntryFactory.create())
        child_private_account = AccountFactory.create(parent=private_account, owner=EntryFactory.create())
        ClaimFactory.create(account=private_account)
        ClaimFactory.create(account=child_private_account)
        return user

    @pytest.mark.parametrize(
        "viewset_class",
        [
            ClaimAPIModelViewSet,
            ClaimRepresentationViewSet,
            ClaimModelViewSet,
            ClaimAccountModelViewSet,
            ClaimProductModelViewSet,
            ClaimEntryModelViewSet,
            ClaimTradeModelViewSet,
            ConsolidatedTradeSummaryTableView,
            ConsolidatedTradeSummaryDistributionChart,
            CumulativeNNMChartView,
            ProfitAndLossPandasView,
        ],
    )
    def test_ensure_permission_on_account(self, account_user, viewset_class):
        """
        We ensure that all claims viewset doesn't show more that what the user is allowed to see.
        For claim, the allowed claim are all the claims where the account is among the account they is allowed to see
        """
        allowed_accounts = Account.objects.filter_for_user(account_user)
        allowed_claims = Claim.objects.filter(account__in=allowed_accounts)

        request = APIRequestFactory().get("")
        request.user = account_user
        viewset = viewset_class(
            request=request,
            kwargs={
                "entry_id": allowed_accounts.first().owner.id,
                "account_id": allowed_accounts.filter(parent__isnull=False).first().id,
                "product_id": allowed_claims.first().product.id,
                "trade_id": allowed_claims.first().trade.id,
            },
        )
        assert allowed_claims.exists()
        assert allowed_claims.count() < Claim.objects.count()  # Ensure that the filtering works
        for claim in viewset.get_queryset():
            assert claim in allowed_claims

    def test_ensure_permission_on_terminal_account_negative_sum_view(
        self, user, negative_claim_factory, account_with_owner_factory
    ):
        entry = Entry.objects.get(id=user.profile.id)

        request = APIRequestFactory().get("")
        request.user = user
        viewset = NegativeTermimalAccountPerProductModelViewSet(request=request)
        # Create a bunch of account and roles
        public_account = account_with_owner_factory.create(is_public=True)
        AccountRoleFactory.create(account=public_account, entry=entry)

        # create two negative claim, one only for an account the user can see
        private_account = account_with_owner_factory.create(is_public=False)
        public_claim = negative_claim_factory.create(account=public_account)  # noqa
        private_claim = negative_claim_factory.create(account=private_account)  # noqa

        assert set(viewset.get_queryset().values_list("account_id", flat=True)) == {public_account.id}

    def test_claim_validate_product_valuations_exist(
        self, claim_factory, super_user, weekday, instrument_price_factory
    ):
        claim = claim_factory.create(create_product_val=False, date=weekday)
        client = APIClient()
        url = reverse("wbportfolio:claim-submit", args=[claim.id])
        client.force_authenticate(user=super_user)
        response = client.patch(url)
        assert response.status_code == 412
        # check that the response contains "date", which means the error was detected on the "date" field
        assert response.json()["date"]

        # test that estimated price don't count
        instrument_price_factory.create(instrument=claim.product, date=weekday, calculated=True)
        response = client.patch(url)
        assert response.status_code == 412

        # With a valid price we can now submit
        instrument_price_factory.create(instrument=claim.product, date=weekday, calculated=False)
        response = client.patch(url)
        assert response.status_code == 200

        url = reverse("wbportfolio:claim-approve", args=[claim.id])
        client.force_authenticate(user=super_user)
        response = client.patch(url)
        assert response.status_code == 200
