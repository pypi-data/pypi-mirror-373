from contextlib import suppress
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db.models import Q
from wbcore.contrib.io.imports import ImportExportHandler
from wbcore.contrib.notifications.dispatch import send_notification

from wbportfolio.models import Portfolio

if TYPE_CHECKING:
    from wbportfolio.models.portfolio_cash_flow import DailyPortfolioCashFlow


class DailyPortfolioCashFlowImportHandler(ImportExportHandler):
    MODEL_APP_LABEL = "wbportfolio.DailyPortfolioCashFlow"

    def _deserialize(self, data):
        data["value_date"] = datetime.strptime(data["value_date"], "%Y-%m-%d").date()
        data["portfolio"] = Portfolio.all_objects.get(id=data["portfolio"])
        if "cash" in data:
            data["cash"] = Decimal(data["cash"])

        if "total_assets" in data:
            data["total_assets"] = Decimal(data["total_assets"])

        if "cash_flow_forecast" in data:
            data["cash_flow_forecast"] = Decimal(data["cash_flow_forecast"])

    def _get_instance(self, data, history=None, **kwargs):
        self.import_source.log += "\nGet Daily Portfolio Cash Flow Instance."
        self.import_source.log += f"\nParameter: Portfolio={data['portfolio']} Value Date={data['value_date']}"

        with suppress(self.model.DoesNotExist):
            return self.model.objects.get(portfolio=data["portfolio"], value_date=data["value_date"])

    def _post_processing_created_object(self, _object: "DailyPortfolioCashFlow"):
        if not _object.portfolio.daily_cashflows.filter(value_date__gt=_object.value_date).exists():
            if _object.proposed_rebalancing != Decimal(0):
                color = "red" if _object.proposed_rebalancing < 0 else "green"
                for user in (
                    get_user_model()
                    .objects.filter(
                        Q(user_permissions__codename="view_dailyportfoliocashflow")
                        | Q(groups__permissions__codename="view_dailyportfoliocashflow")
                    )
                    .distinct()
                ):
                    send_notification(
                        code="wbportfolio.dailyportfoliocashflow.notify_rebalance",
                        title=f"Proposed Rebalancing in the portfolio: {_object.portfolio}",
                        body=f"The workbench proposes to rebalance the portfolio {_object.portfolio} by <span style='color:{color}'>{_object.proposed_rebalancing:+,.2f}</span>",
                        user=user,
                        reverse_name="wbportfolio:portfoliocashflow-detail",
                        reverse_args=[_object.pk],
                    )
