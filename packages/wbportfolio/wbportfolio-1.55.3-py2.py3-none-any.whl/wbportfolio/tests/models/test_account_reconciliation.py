from datetime import date
from typing import TYPE_CHECKING

import pytest
from django.db import IntegrityError
from wbcrm.models import Account

from wbportfolio.models import AccountReconciliation, Claim
from wbportfolio.models.products import Product
from wbportfolio.models.reconciliations.account_reconciliation_lines import (
    AccountReconciliationLine,
)

if TYPE_CHECKING:
    from wbcore.contrib.authentication.models import User

    from wbportfolio.factories import AccountReconciliationLineFactory, ClaimFactory


class TestAccountReconciliation:
    def test_str(self):
        account = Account(computed_str="Test Account")
        reconciliation = AccountReconciliation(account=account, reconciliation_date=date(2021, 1, 1))
        assert str(reconciliation) == "Test Account (01.01.2021)"

    def test_get_endpoint_basename(self):
        assert AccountReconciliation.get_endpoint_basename() == "wbportfolio:accountreconciliation"

    def test_get_representation_endpoint(self):
        assert (
            AccountReconciliation.get_representation_endpoint()
            == "wbportfolio:accountreconciliationrepresentation-list"
        )

    def test_get_representation_value_key(self):
        assert AccountReconciliation.get_representation_value_key() == "id"

    def test_get_representation_label_key(self):
        assert AccountReconciliation.get_representation_label_key() == "{{account}} {{reconciliation_date}}"

    @pytest.mark.django_db
    def test_create_for_date_and_account(self, claim_factory: "ClaimFactory", account: Account, user: "User"):
        for _ in range(10):
            claim_factory.create(account=account, date=date(2020, 12, 30), status=Claim.Status.APPROVED)

        AccountReconciliation.objects.create(
            reconciliation_date=date(2021, 1, 1),
            account=account,
            creator=user,
        )

        assert (
            AccountReconciliationLine.objects.count() == Claim.objects.distinct("product").count()
        ), "There should be as many lines as unique products for claims"


class TestAccountReconciliationLine:
    def test_str(self):
        account = Account(computed_str="Test Account")
        reconciliation = AccountReconciliation(account=account, reconciliation_date=date(2021, 1, 1))
        product = Product(computed_str="Test Product")
        line = AccountReconciliationLine(reconciliation=reconciliation, product=product, shares=100)

        assert str(line) == "Test Account (01.01.2021): Test Product 100 shares"

    def test_get_endpoint_basename(self):
        assert AccountReconciliationLine.get_endpoint_basename() == "wbportfolio:accountreconciliationline"

    def test_representation_endpoint(self):
        assert (
            AccountReconciliationLine.get_representation_endpoint()
            == "wbportfolio:accountreconciliationlinerepresentation-list"
        )

    def test_representation_value_key(self):
        assert AccountReconciliationLine.get_representation_value_key() == "id"

    def test_representation_label_key(self):
        assert AccountReconciliationLine.get_representation_label_key() == "{{reconciliation}}"

    def test_save_calculate_nominal_value(self, mocker):
        mocker.patch("django.db.models.Model.save")
        product = Product(share_price=100)
        line = AccountReconciliationLine(product=product, shares=100, nominal_value=None)
        line.save()

        assert line.nominal_value == 100 * 100

    def test_save_calculate_shares(self, mocker):
        mocker.patch("django.db.models.Model.save")
        product = Product(share_price=100)
        line = AccountReconciliationLine(product=product, nominal_value=10000, shares=None)
        line.save()

        assert line.shares == 100

    def test_save_calculate_nominal_value_external(self, mocker):
        mocker.patch("django.db.models.Model.save")
        product = Product(share_price=100)
        line = AccountReconciliationLine(product=product, shares_external=100, nominal_value_external=None)
        line.save()

        assert line.nominal_value_external == 100 * 100

    def test_save_calculate_shares_external(self, mocker):
        mocker.patch("django.db.models.Model.save")
        product = Product(share_price=100)
        line = AccountReconciliationLine(product=product, nominal_value_external=10000, shares_external=None)
        line.save()

        assert line.shares_external == 100

    @pytest.mark.django_db
    def test_unique_constraint(
        self,
        account_reconciliation: AccountReconciliation,
        product: Product,
        account_reconciliation_line_factory: "AccountReconciliationLineFactory",
    ):
        account_reconciliation_line_factory.create(reconciliation=account_reconciliation, product=product)
        with pytest.raises(IntegrityError):
            account_reconciliation_line_factory.create(reconciliation=account_reconciliation, product=product)

    @pytest.mark.django_db
    def test_currency_annotation(self, account_reconciliation_line: AccountReconciliationLine):
        assert (
            AccountReconciliationLine.objects.all().annotate_currency().first().currency
            == account_reconciliation_line.product.currency.symbol
        )

    @pytest.mark.django_db
    def test_assets_under_management_annotation(self, account_reconciliation_line: AccountReconciliationLine):
        assert (
            AccountReconciliationLine.objects.all().annotate_assets_under_management().first().assets_under_management
            == account_reconciliation_line.shares * account_reconciliation_line.price
        )

    @pytest.mark.django_db
    def test_assets_under_management_external_annotation(self, account_reconciliation_line: AccountReconciliationLine):
        assert (
            AccountReconciliationLine.objects.all()
            .annotate_assets_under_management_external()
            .first()
            .assets_under_management_external
            == account_reconciliation_line.shares_external * account_reconciliation_line.price
        )

    @pytest.mark.django_db
    @pytest.mark.parametrize("account_reconciliation_line__shares", [100])
    @pytest.mark.parametrize("account_reconciliation_line__shares_external", [101])
    def test_is_not_equal_annotation(self, account_reconciliation_line: AccountReconciliationLine):
        assert not AccountReconciliationLine.objects.all().annotate_is_equal().first().is_equal

    @pytest.mark.django_db
    @pytest.mark.parametrize("account_reconciliation_line__shares", [100])
    @pytest.mark.parametrize("account_reconciliation_line__shares_external", [100])
    def test_is_equal_annotation(self, account_reconciliation_line: AccountReconciliationLine):
        assert AccountReconciliationLine.objects.all().annotate_is_equal().first().is_equal

    @pytest.mark.django_db
    def test_shares_diff_annotation(self, account_reconciliation_line: AccountReconciliationLine):
        assert (
            AccountReconciliationLine.objects.all().annotate_shares_diff().first().shares_diff
            == account_reconciliation_line.shares_external - account_reconciliation_line.shares
        )

    @pytest.mark.django_db
    def test_pct_diff_annotation(self, account_reconciliation_line: AccountReconciliationLine):
        assert (
            AccountReconciliationLine.objects.all().annotate_pct_diff().first().pct_diff
            == (account_reconciliation_line.shares_external - account_reconciliation_line.shares)
            / account_reconciliation_line.shares
        )

    @pytest.mark.django_db
    def test_nominal_value_diff_annotation(self, account_reconciliation_line: AccountReconciliationLine):
        assert (
            AccountReconciliationLine.objects.all().annotate_nominal_value_diff().first().nominal_value_diff
            == account_reconciliation_line.nominal_value_external - account_reconciliation_line.nominal_value
        )

    @pytest.mark.django_db
    def test_assets_under_management_diff_annotation(self, account_reconciliation_line: AccountReconciliationLine):
        assert (
            AccountReconciliationLine.objects.all()
            .annotate_assets_under_management()
            .annotate_assets_under_management_external()
            .annotate_assets_under_management_diff()
            .first()
            .assets_under_management_diff
            == (account_reconciliation_line.shares_external * account_reconciliation_line.price)
            - (account_reconciliation_line.shares * account_reconciliation_line.price)
        )
