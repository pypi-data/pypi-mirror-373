import pytest
from faker import Faker
from pandas.tseries.offsets import BDay
from psycopg.types.range import NumericRange
from wbcompliance.factories.risk_management import RuleThresholdFactory

from wbportfolio.models.transactions.claim import ClaimGroupbyChoice
from wbportfolio.risk_management.backends.accounts import (
    RuleBackend as AccountRuleBackend,
)

fake = Faker()


@pytest.mark.django_db
class TestAccountRuleModel:
    @pytest.fixture
    def account_backend(
        self,
        entry,
        weekday,
        business_days_interval,
        group_by=ClaimGroupbyChoice.ACCOUNT.name,
        extra_parameters=None,
    ):
        parameters = {"group_by": group_by, "business_days_interval": business_days_interval, "field": "SHARES"}
        if extra_parameters:
            parameters.update(extra_parameters)
        return AccountRuleBackend(
            weekday,
            entry,
            parameters,
            [RuleThresholdFactory.create(range=NumericRange(lower=None, upper=-0.2))],  # detect any -20% perf
        )

    @pytest.mark.parametrize(
        "business_days_interval",
        [7],
    )
    def test_check_rule_groupby_account(
        self,
        weekday,
        entry,
        business_days_interval,
        product,
        claim_factory,
        customer_trade_factory,
        account_factory,
        account_backend,
    ):
        # Simple test to test if a valid drop in performance outside the rule window will not be detected but a one within will.
        account = account_factory.create(owner=entry)
        other_account = account_factory.create()
        claim_factory.create(
            date=(weekday - BDay(business_days_interval + 3)).date(),
            account=account,
            trade=customer_trade_factory.create(
                underlying_instrument=product, transaction_date=(weekday - BDay(business_days_interval + 3)).date()
            ),
            status="APPROVED",
            shares=100,
        )
        claim_factory.create(
            date=(weekday - BDay(business_days_interval + 2)).date(),
            account=account,
            trade=customer_trade_factory.create(
                underlying_instrument=product, transaction_date=(weekday - BDay(business_days_interval + 2)).date()
            ),
            status="APPROVED",
            shares=-50,
        )  # this drop should not be detected

        claim_factory.create(
            date=(weekday - BDay(business_days_interval + 1)).date(),
            account=account,
            trade=customer_trade_factory.create(
                underlying_instrument=product, transaction_date=(weekday - BDay(business_days_interval + 1)).date()
            ),
            status="APPROVED",
            shares=150,
        )
        claim_factory.create(
            date=(weekday - BDay(1)).date(),
            account=account,
            trade=customer_trade_factory.create(
                underlying_instrument=product, transaction_date=(weekday - BDay(1)).date()
            ),
            status="APPROVED",
            shares=-50,
        )  # this drop should be detected

        claim_factory.create(
            date=(weekday - BDay(business_days_interval + 1)).date(),
            account=other_account,
            trade=customer_trade_factory.create(
                underlying_instrument=product, transaction_date=(weekday - BDay(business_days_interval + 1)).date()
            ),
            status="APPROVED",
            shares=150,
        )
        claim_factory.create(
            date=(weekday - BDay(1)).date(),
            account=other_account,
            trade=customer_trade_factory.create(
                underlying_instrument=product, transaction_date=(weekday - BDay(1)).date()
            ),
            status="APPROVED",
            shares=-50,
        )  # this drop is valid but an another account so won't be detected
        res = list(account_backend.check_rule())
        assert len(res) == 1
