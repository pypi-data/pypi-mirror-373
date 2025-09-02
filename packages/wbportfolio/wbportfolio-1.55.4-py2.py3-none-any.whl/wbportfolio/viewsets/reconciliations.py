from collections import defaultdict
from itertools import product
from typing import TYPE_CHECKING

import pandas as pd
from django.db.models import Exists, F, OuterRef, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcore import viewsets
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.utils.strings import format_number

from wbportfolio.models import AccountReconciliation, AccountReconciliationLine
from wbportfolio.models.reconciliations.account_reconciliation_lines import (
    AccountReconciliationLineQuerySet,
)
from wbportfolio.serializers import (
    AccountReconciliationLineModelSerializer,
    AccountReconciliationModelSerializer,
)
from wbportfolio.viewsets.configs.buttons import (
    AccountReconciliationButtonViewConfig,
    AccountReconciliationLineButtonViewConfig,
)
from wbportfolio.viewsets.configs.display import (
    AccountReconciliationDisplayViewConfig,
    AccountReconciliationLineDisplayViewConfig,
)
from wbportfolio.viewsets.configs.endpoints.reconciliations import (
    AccountReconciliationEndpointViewConfig,
    AccountReconciliationLineEndpointViewConfig,
)

if TYPE_CHECKING:
    from rest_framework.request import Request


class AccountReconciliationModelViewSet(viewsets.ModelViewSet):
    INSTANCE_DOCUMENTATION = "wbportfolio/markdown/documentation/account_holding_reconciliation.md"

    queryset = AccountReconciliation.objects.all()
    serializer_class = AccountReconciliationModelSerializer
    display_config_class = AccountReconciliationDisplayViewConfig
    button_config_class = AccountReconciliationButtonViewConfig
    endpoint_config_class = AccountReconciliationEndpointViewConfig

    filterset_fields = {
        "account": ["exact"],
        "creator": ["exact"],
        "approved_by": ["exact"],
        "reconciliation_date": ["gte", "exact", "lte"],
        "approved_dt": ["gte", "lte"],
    }
    ordering = ordering_fields = ["-reconciliation_date"]

    def get_queryset(self):
        return (
            AccountReconciliation.objects.filter_for_user(self.request.user)
            .annotate(
                unequal_exists=Exists(
                    AccountReconciliationLine.objects.filter(
                        Q(reconciliation_id=OuterRef("pk")) & ~Q(shares=F("shares_external"))
                    )
                )
            )
            .select_related("account")
            .select_related("creator")
            .select_related("creator__profile")
            .select_related("approved_by")
            .select_related("approved_by__profile")
        )

    @action(methods=["PATCH"], detail=True)
    def agree_customer(self, request: "Request", pk: int | None = None) -> Response:
        reconciliation = self.get_object()
        if reconciliation and isinstance(reconciliation, AccountReconciliation):
            reconciliation.approved_by = request.user
            reconciliation.approved_dt = timezone.now()
            reconciliation.save()
            send_notification(
                code="wbportfolio.account_reconciliation.notify",
                title=f"{reconciliation.approved_by} has agreed to the calculations for the account {reconciliation.account}.",
                body=f"The account {reconciliation.account} has been reconciled and the calculations have been agreed to by {reconciliation.approved_by}. You may proceed.",
                user=reconciliation.creator,
                reverse_name="wbportfolio:accountreconciliation-detail",
                reverse_args=[reconciliation.id],
            )
            return Response({"__notification": "You have aggreed to the calculations, thank you."})
        return Response(
            {"__notification": "There has been an issue with agreeing to the calculations."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(methods=["PATCH"], detail=True)
    def disagree_customer(self, request: "Request", pk: int | None = None) -> Response:
        reconciliation = self.get_object()
        if reconciliation and isinstance(reconciliation, AccountReconciliation):
            send_notification(
                code="wbportfolio.account_reconciliation.notify",
                title=f"{request.user} has disagreed with your calculations for the account {reconciliation.account}",
                body=f"Please reach out to {request.user} to adjust the reconciliation.",
                user=reconciliation.creator,
                reverse_name="wbportfolio:accountreconciliation-detail",
                reverse_args=[reconciliation.id],
            )
        return Response()

    @action(methods=["PATCH"], detail=True)
    def recompute(self, request: "Request", pk: int | None = None) -> Response:
        AccountReconciliationLine.objects.update_or_create_for_reconciliation(self.get_object())
        return Response()

    @action(methods=["PATCH"], detail=True)
    def notify(self, request: "Request", pk: int | None = None) -> Response:
        try:
            self.get_object().notify(update=True, silent_errors=False)
            return Response()
        except ValueError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class AccountReconciliationLineModelViewSet(viewsets.ModelViewSet):
    DEPENDANT_IDENTIFIER = ["wbportfolio:accountreconciliation"]

    queryset = AccountReconciliationLine.objects.all()
    serializer_class = AccountReconciliationLineModelSerializer
    display_config_class = AccountReconciliationLineDisplayViewConfig
    button_config_class = AccountReconciliationLineButtonViewConfig
    endpoint_config_class = AccountReconciliationLineEndpointViewConfig

    def get_aggregates(self, queryset, paginated_queryset):
        fields = [
            "assets_under_management",
            "assets_under_management_external",
            "assets_under_management_diff",
        ]
        df = pd.DataFrame(queryset.values("currency_key", *fields))
        aggregates = defaultdict(dict)
        if not df.empty:
            for field in fields:
                aggregates[field]["Your"] = "Total AuM"

            for currency_symbol, field in product(df.currency_key.unique(), fields):
                dff = df.loc[df["currency_key"] == currency_symbol]
                aggregates[field][f"{currency_symbol}"] = format_number(dff[field].sum())

        return aggregates

    def get_queryset(self) -> "AccountReconciliationLineQuerySet":
        queryset: "AccountReconciliationLineQuerySet" = super().get_queryset()

        if accountreconciliation_id := self.kwargs.get("accountreconciliation_id"):
            queryset = queryset.filter(reconciliation_id=accountreconciliation_id)

        return (
            queryset.annotate_currency()
            .annotate_currency_key()
            .annotate_assets_under_management()
            .annotate_assets_under_management_external()
            .annotate_shares_diff()
            .annotate_nominal_value_diff()
            .annotate_assets_under_management_diff()
            .annotate_pct_diff()
            .annotate_is_equal()
            .select_related("reconciliation")
            .select_related("reconciliation__account")
            .select_related("product")
        )
