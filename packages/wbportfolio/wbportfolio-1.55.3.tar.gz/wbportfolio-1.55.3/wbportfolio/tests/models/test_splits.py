from decimal import Decimal
from unittest.mock import patch

import pytest
from faker import Faker
from pandas.tseries.offsets import BDay

from wbportfolio.factories import AdjustmentFactory
from wbportfolio.models import Adjustment, PortfolioRole
from wbportfolio.models.adjustments import post_adjustment_on_prices

fake = Faker()


@pytest.mark.django_db
class TestAdjustmentModel:
    @pytest.fixture()
    def applied_adjustment(self):
        return AdjustmentFactory.create(status=Adjustment.Status.APPLIED)

    @pytest.fixture()
    def old_adjustment(self):
        return AdjustmentFactory.create(status=Adjustment.Status.PENDING, date=fake.past_date())

    # Test utilities function
    @patch("wbportfolio.models.adjustments.chain")
    def test_adjustment_creation(
        self,
        mock_fct,
        user_factory,
        adjustment_factory,
        product_portfolio_role_factory,
        asset_position_factory,
        instrument,
    ):
        user_factory.create()  # User without permission
        user_porftolio_manager = user_factory.create()
        product_portfolio_role_factory.create(
            person=user_porftolio_manager.profile, role_type=PortfolioRole.RoleType.PORTFOLIO_MANAGER
        )
        asset_position_factory.create(underlying_instrument=instrument)
        adjustment2 = adjustment_factory.create(instrument=instrument, date=fake.past_date())
        assert mock_fct.call_count == 1
        assert adjustment2.status == Adjustment.Status.PENDING

        # If newly created instrument's adjustment happens in the future, its state becomes pending and an import task is triggered
        adjustment1 = adjustment_factory.create(instrument=instrument)
        assert adjustment1.status == Adjustment.Status.PENDING
        assert mock_fct.call_count == 2

    def test_cumulative_factor(self, adjustment_factory):
        """
        s1 -> s2 -> s3
        """
        s3 = adjustment_factory.create(status=Adjustment.Status.APPLIED)
        s3.refresh_from_db()
        assert s3.cumulative_factor == Decimal(1.0)

        s2 = adjustment_factory.create(
            status=Adjustment.Status.APPLIED, instrument=s3.instrument, date=s3.date - BDay(1)
        )
        s1 = adjustment_factory.create(
            instrument=s3.instrument, date=s3.date - BDay(2)
        )  # This adjustment is not applied and shouldn't be accounted for in the cumulative factor of the futures adjustments
        s3.refresh_from_db()
        s2.refresh_from_db()
        s1.refresh_from_db()
        assert s2.cumulative_factor == pytest.approx(
            s3.factor, rel=Decimal(1e-3)
        )  # Normal case, applied adjustment cumulative factor should reflect the parent factors
        assert s1.cumulative_factor == pytest.approx(
            s2.factor * s3.factor, rel=Decimal(1e-3)
        )  # even if not applied, cumulative factor is computed normally

    def test_apply_adjustment_on_assets(self, adjustment, asset_position_factory):
        a1 = asset_position_factory.create(
            underlying_instrument=adjustment.instrument, date=adjustment.adjustment_date
        )
        a2 = asset_position_factory.create(underlying_instrument=adjustment.instrument, date=adjustment.date)
        adjustment.apply_adjustment_on_assets()
        a1.refresh_from_db()
        a2.refresh_from_db()
        assert a1.applied_adjustment == adjustment
        assert not a2.applied_adjustment

    def test_future_adjustment_not_applied_on_assets(self, adjustment, asset_position_factory):
        p = asset_position_factory.create(
            underlying_instrument=adjustment.instrument, date=(adjustment.date + BDay(1)).date()
        )

        adjustment.apply_adjustment_on_assets()
        p.refresh_from_db()
        assert not p.applied_adjustment

    def test_adjustment_played_out_of_order(self, adjustment_factory, asset_position_factory):
        s1 = adjustment_factory.create()
        s2 = adjustment_factory.create(instrument=s1.instrument, date=(s1.date + BDay(2)).date())

        a0 = asset_position_factory.create(underlying_instrument=s1.instrument, date=s2.adjustment_date - BDay(3))
        a1 = asset_position_factory.create(
            underlying_instrument=s1.instrument, date=s2.adjustment_date - BDay(2), applied_adjustment=s2
        )
        a2 = asset_position_factory.create(
            underlying_instrument=s1.instrument, date=s2.adjustment_date - BDay(1), applied_adjustment=s2
        )
        a3 = asset_position_factory.create(
            underlying_instrument=s1.instrument, date=s2.adjustment_date, applied_adjustment=s2
        )

        s1.apply_adjustment_on_assets()
        a0.refresh_from_db()
        a1.refresh_from_db()
        a2.refresh_from_db()
        a3.refresh_from_db()

        assert a0.applied_adjustment == s1
        assert a1.applied_adjustment == s1
        assert a2.applied_adjustment == s2
        assert a3.applied_adjustment == s2

    # Test Basic FSM workflow
    @patch("wbportfolio.models.adjustments.apply_adjustment_on_assets_as_task.delay")
    def test_apply(self, mock_fct, old_adjustment):
        assert mock_fct.call_count == 0
        old_adjustment.apply()
        old_adjustment.save()
        assert old_adjustment.status == Adjustment.Status.APPLIED
        mock_fct.assert_called()

    def test_deny(self, old_adjustment, user):
        assert old_adjustment.status == Adjustment.Status.PENDING
        old_adjustment.deny(by=user)
        old_adjustment.save()
        assert old_adjustment.last_handler == user.profile
        assert old_adjustment.status == Adjustment.Status.DENIED

    @patch("wbportfolio.models.adjustments.revert_adjustment_on_assets_as_task.delay")
    def test_revert(self, mock_fct, adjustment_factory):
        adjustment = adjustment_factory.create(status=Adjustment.Status.APPLIED)
        assert mock_fct.call_count == 0
        adjustment.revert()
        adjustment.save()
        assert adjustment.status == Adjustment.Status.PENDING
        mock_fct.assert_called_with(adjustment.id)

    def test_revert_adjustment_on_assets(self, adjustment_factory, asset_position_factory):
        s1 = adjustment_factory.create(status=Adjustment.Status.APPLIED)
        s2 = adjustment_factory.create(
            date=s1.date + BDay(1), instrument=s1.instrument, status=Adjustment.Status.APPLIED
        )
        s3 = adjustment_factory.create(
            date=s2.date + BDay(1), instrument=s1.instrument, status=Adjustment.Status.APPLIED
        )

        a1 = asset_position_factory.create(
            underlying_instrument=s1.instrument, date=s1.adjustment_date, applied_adjustment=s1
        )
        a2 = asset_position_factory.create(
            underlying_instrument=s1.instrument, date=s2.adjustment_date, applied_adjustment=s2
        )
        a3 = asset_position_factory.create(
            underlying_instrument=s1.instrument, date=s3.adjustment_date, applied_adjustment=s3
        )

        s1.revert_adjustment_on_assets()
        a1.refresh_from_db()
        a2.refresh_from_db()
        a3.refresh_from_db()
        assert a1.applied_adjustment == s2
        assert a2.applied_adjustment == s2
        assert a3.applied_adjustment == s3

        s2.revert_adjustment_on_assets()
        a1.refresh_from_db()
        a2.refresh_from_db()
        a3.refresh_from_db()
        assert a1.applied_adjustment == s3
        assert a2.applied_adjustment == s3
        assert a3.applied_adjustment == s3

        s3.revert_adjustment_on_assets()
        a1.refresh_from_db()
        a2.refresh_from_db()
        a3.refresh_from_db()
        assert not a1.applied_adjustment
        assert not a2.applied_adjustment
        assert not a3.applied_adjustment

    def test_post_adjustment_on_prices_without_assets(self, adjustment):
        post_adjustment_on_prices(adjustment.id)
        adjustment.refresh_from_db()
        assert adjustment.status == Adjustment.Status.APPLIED

    @patch.object(Adjustment, "automatically_applied_adjustments_on_assets")
    def test_post_adjustment_automatically_approve_on_prices_with_assets(
        self,
        mock_check_fct,
        adjustment,
        asset_position_factory,
    ):
        a1 = asset_position_factory.create(
            underlying_instrument=adjustment.instrument, date=adjustment.adjustment_date
        )
        mock_check_fct.return_value = True
        post_adjustment_on_prices(adjustment.id)
        a1.refresh_from_db()
        adjustment.refresh_from_db()
        a1.applied_adjustment == adjustment
        assert adjustment.status == Adjustment.Status.APPLIED

    @patch("wbportfolio.models.adjustments.send_notification")
    @patch.object(Adjustment, "automatically_applied_adjustments_on_assets")
    def test_post_adjustment_not_automatically_approve_on_prices_with_assets(
        self,
        mock_check_fct,
        mock_delay_fct,
        adjustment,
        asset_position_factory,
        user_factory,
        product_portfolio_role_factory,
    ):
        asset_position_factory.create(
            underlying_instrument=adjustment.instrument, date=(adjustment.date - BDay(1)).date()
        )
        user_factory.create()  # User without permission
        user_porftolio_manager = user_factory.create()
        product_portfolio_role_factory.create(
            person=user_porftolio_manager.profile, role_type=PortfolioRole.RoleType.PORTFOLIO_MANAGER
        )
        mock_check_fct.return_value = False
        post_adjustment_on_prices(adjustment.id)
        adjustment.refresh_from_db()
        mock_delay_fct.call_args[0] == user_porftolio_manager.id
        assert adjustment.status == Adjustment.Status.PENDING
