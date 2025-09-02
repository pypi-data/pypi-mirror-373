from contextlib import suppress
from datetime import date

from pandas._libs.tslibs.offsets import BDay
from wbcore import serializers as wb_serializers
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)

from wbportfolio.models import AssetPosition, Portfolio
from wbportfolio.serializers import RebalancerModelSerializer
from wbportfolio.viewsets.configs.display.rebalancing import RebalancerDisplayConfig


class CreateModelPortfolioSerializer(wb_serializers.ModelSerializer):
    create_index = wb_serializers.BooleanField(default=False, label="Create Underlying Index")
    name = wb_serializers.CharField(required=True)
    _currency = CurrencyRepresentationSerializer(source="currency")

    class Meta:
        model = Portfolio
        fields = (
            "name",
            "currency",
            "create_index",
            "_currency",
        )


def _get_portfolio_start_end_serializer_class(portfolio):
    today = date.today()

    class StartEndDateSerializer(wb_serializers.Serializer):
        start = wb_serializers.DateField(
            label="Start",
            default=portfolio.assets.earliest("date").date if portfolio.assets.exists() else today,
        )
        end = wb_serializers.DateField(
            label="End", default=portfolio.assets.latest("date").date if portfolio.assets.exists() else today
        )

    return StartEndDateSerializer


def _get_rebalance_serializer_class(portfolio):
    try:
        default_trade_date = (portfolio.assets.latest("date").date + BDay(1)).date()
    except AssetPosition.DoesNotExist:
        default_trade_date = date.today()

    class RebalanceSerializer(wb_serializers.Serializer):
        trade_date = wb_serializers.DateField(default=default_trade_date)

    return RebalanceSerializer


class PortfolioButtonConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        admin_buttons = [
            bt.ActionButton(
                method=RequestType.POST,
                identifiers=("wbportfolio:portfolio",),
                key="add_automatic_rebalancer",
                label="Attach Rebalancer",
                serializer=RebalancerModelSerializer,
                action_label="Attach Rebalancer",
                title="Attach Rebalancer",
                instance_display=RebalancerDisplayConfig(
                    self.view, self.request, self.instance
                ).get_instance_display(),
            )
        ]
        buttons = [bt.WidgetButton(key="treegraphchart", label="Visualize Tree Graph Chart")]
        with suppress(Portfolio.DoesNotExist, KeyError):
            portfolio = Portfolio.objects.get(id=self.view.kwargs["pk"])
            buttons.append(
                bt.ActionButton(
                    method=RequestType.POST,
                    identifiers=("wbportfolio:portfolio",),
                    key="rebalance",
                    label="Rebalance",
                    serializer=_get_rebalance_serializer_class(portfolio),
                    action_label="Rebalance",
                    title="Rebalance",
                    instance_display=create_simple_display([["trade_date"]]),
                )
            )

            if primary_portfolio := portfolio.primary_portfolio:
                admin_buttons.append(
                    bt.ActionButton(
                        method=RequestType.POST,
                        identifiers=("wbportfolio:portfolio",),
                        key="recompute_lookthrough",
                        label="Recompute Look-Through Portfolio",
                        serializer=_get_portfolio_start_end_serializer_class(primary_portfolio),
                        action_label="Recompute Look-Through Portfolio",
                        title="Recompute Look-Through Portfolio",
                        instance_display=create_simple_display([["start", "end"]]),
                    )
                )
            buttons.append(
                bt.DropDownButton(label="Admin", icon=WBIcon.UNFOLD.icon, buttons=tuple(admin_buttons)),
            )
        return set(buttons)

    def get_custom_list_instance_buttons(self):
        return self.get_custom_instance_buttons()

    # def get_custom_buttons(self):
    #     if not self.view.kwargs.get("pk", None):
    #         return {
    #             bt.ActionButton(
    #                 method=RequestType.POST,
    #                 identifiers=("wbportfolio:portfolio",),
    #                 endpoint=reverse("wbportfolio:portfolio-createmodelportfolio", request=self.request),
    #                 label="Create New Model Portfolio",
    #                 serializer=CreateModelPortfolioSerializer,
    #                 action_label="create",
    #                 title="Create Model Portfolio",
    #                 instance_display=create_simple_display([["name", "currency"], ["create_index", "."]]),
    #             )
    #         }
    #     return set()
