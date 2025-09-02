from datetime import date

from django.dispatch import receiver
from rest_framework.reverse import reverse
from wbcore.contrib.directory.serializers import (
    CompanyModelSerializer,
    EntryModelSerializer,
    PersonModelSerializer,
)
from wbcore.filters.defaults import current_quarter_date_start
from wbcore.signals import add_instance_additional_resource
from wbcrm.serializers.accounts import AccountModelSerializer
from wbfdm.serializers import InstrumentModelSerializer

from wbportfolio.models import PortfolioRole, Trade
from wbportfolio.serializers.products import ProductModelSerializer


@receiver(add_instance_additional_resource, sender=InstrumentModelSerializer)
@receiver(add_instance_additional_resource, sender=ProductModelSerializer)
def add_instrument_serializer_resources(sender, serializer, instance, request, user, **kwargs):
    additional_resources = dict()

    has_assets = any([i.assets.exists() for i in instance.get_descendants(include_self=True)])
    if PortfolioRole.is_portfolio_manager(user.profile) and has_assets:
        additional_resources["assets"] = reverse(
            "wbportfolio:instrument-asset-list", args=[instance.id], request=request
        )
        additional_resources["assetschart"] = reverse(
            "wbportfolio:instrument-assetpositionchart-list", args=[instance.id], request=request
        )

    if instance.portfolios.exists():
        additional_resources["distribution_chart"] = reverse(
            "wbportfolio:portfolio-distributionchart-list", args=[instance.portfolio.id], request=request
        )
        additional_resources["distribution_table"] = reverse(
            "wbportfolio:portfolio-distributiontable-list", args=[instance.portfolio.id], request=request
        )

    if user.profile.is_internal or user.is_superuser:
        if Trade.valid_customer_trade_objects.filter(underlying_instrument=instance).exists():
            additional_resources["instrument_subscriptionsredemptions"] = reverse(
                "wbportfolio:instrument-subscriptionredemption-list", args=[instance.id], request=request
            )
        if (
            Trade.objects.filter(underlying_instrument__in=instance.get_descendants(include_self=True))
            .exclude(transaction_subtype__in=[Trade.Type.REDEMPTION, Trade.Type.SUBSCRIPTION])
            .exists()
        ):
            additional_resources["instrument_trades"] = (
                f'{reverse("wbportfolio:instrument-trade-list", args=[instance.id], request=request)}?is_customer_trade=False'
            )

    if PortfolioRole.is_manager(user.profile):
        additional_resources["portfoliorole"] = reverse(
            "wbportfolio:instrument-portfoliorole-list", args=[instance.id], request=request
        )
    return additional_resources


@receiver(add_instance_additional_resource, sender=InstrumentModelSerializer)
@receiver(add_instance_additional_resource, sender=ProductModelSerializer)
def asset_portfolio_resources(sender, serializer, instance, request, user, **kwargs):
    additional_resources = dict()
    portfolio = instance.portfolio

    if portfolio and portfolio.assets.exists():
        if PortfolioRole.is_analyst(user.profile, portfolio=portfolio):
            additional_resources["portfolio_positions"] = reverse(
                "wbportfolio:portfolio-asset-list", args=[portfolio.id], request=request
            )
            additional_resources["portfolio_positions_contributors"] = reverse(
                "wbportfolio:portfolio-contributor-list",
                args=[portfolio.id],
                request=request,
            )
    return additional_resources


@receiver(add_instance_additional_resource, sender=InstrumentModelSerializer)
@receiver(add_instance_additional_resource, sender=ProductModelSerializer)
def transactions_resources(sender, serializer, instance, request, user, **kwargs):
    additional_resources = dict()
    portfolio = instance.primary_portfolio
    if portfolio:
        if portfolio.trades.exists() and user.profile.is_internal:
            additional_resources["portfolio_subscriptionsredemptions"] = (
                f'{reverse("wbportfolio:portfolio-trade-list", args=[portfolio.id], request=request)}?is_customer_trade=True'
            )
            additional_resources["portfolio_trades"] = (
                f'{reverse("wbportfolio:portfolio-trade-list", args=[portfolio.id], request=request)}?is_customer_trade=False'
            )

    return additional_resources


@receiver(add_instance_additional_resource, sender=ProductModelSerializer)
def product_resources(sender, serializer, instance, request, user, **kwargs):
    additional_resources = dict()
    if user.profile.is_internal or user.is_superuser:
        additional_resources["custodiandistribution"] = reverse(
            "wbportfolio:instrument-custodiandistribution-list",
            args=[instance.id],
            request=request,
        )
        additional_resources["customerdistribution"] = reverse(
            "wbportfolio:instrument-customerdistribution-list",
            args=[instance.id],
            request=request,
        )
        additional_resources["tradechart"] = reverse(
            "wbportfolio:product-nominalchart-list",
            args=[instance.id],
            request=request,
        )
        additional_resources["aumchart"] = reverse(
            "wbportfolio:product-aumchart-list",
            args=[instance.id],
            request=request,
        )
    if instance.fees.exists() and PortfolioRole.is_portfolio_manager(user.profile, instrument=instance):
        additional_resources["product_fees"] = reverse(
            "wbportfolio:product-fees-list", args=[instance.id], request=request
        )
        additional_resources["product_aggregatedfees"] = reverse(
            "wbportfolio:product-feesaggregated-list", args=[instance.id], request=request
        )

    return additional_resources


@receiver(add_instance_additional_resource, sender=CompanyModelSerializer)
@receiver(add_instance_additional_resource, sender=PersonModelSerializer)
@receiver(add_instance_additional_resource, sender=EntryModelSerializer)
def claim_adding_additional_resource(sender, serializer, instance, request, user, **kwargs):
    start = current_quarter_date_start()
    return {
        "claims": reverse("wbportfolio:entry-claim-list", args=[instance.id], request=request),
        "aum": f'{reverse("wbportfolio:aumtable-list", args=[], request=request)}?group_by=PRODUCT&account_owner={instance.id}&date={start:%Y-%m-%d},{date.today():%Y-%m-%d}',
    }


@receiver(add_instance_additional_resource, sender=AccountModelSerializer)
def account_reconciliation_resource(sender, serializer, instance, request, user, **kwargs):
    return {
        "wbportfolio-accountreconciliation": f'{reverse("wbportfolio:accountreconciliation-list", request=request)}?account={instance.id}',
        "wbportfolio-reconcile-account": f'{reverse("wbportfolio:accountreconciliation-list", request=request)}?account={instance.id}',
    }
