from typing import TYPE_CHECKING, Any

from django.db.models import F, FloatField, Sum
from django.db.models.functions import Cast, ExtractYear
from langchain_core.messages import HumanMessage, SystemMessage
from wbfdm.models import Instrument

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage
    from wbcrm.models import Account


def get_holding_prompt(account: "Account") -> tuple[list["BaseMessage"], dict[str, Any]]:
    from wbportfolio.models import Product
    from wbportfolio.models.transactions.claim import Claim

    products = (
        Claim.get_valid_and_approved_claims(account=account)
        .distinct("product")
        .values_list("product", "product__isin")
    )

    performances = {}
    for product_id, product_name in products:
        performances[product_name] = (
            Instrument.extract_annual_performance_df(Product.objects.get(id=product_id).get_prices_df())
            .set_index("year")["performance"]
            .to_dict()
        )

    return [
        SystemMessage(
            "The following products are held by the account holder. Analyze their performances and check correlations between the holdings and their performances/interactions."
        ),
        HumanMessage("Performances per product ISIN per year: {performances}"),
    ], {"performances": performances}


def get_performances_prompt(account: "Account") -> tuple[list["BaseMessage"], dict[str, Any]]:
    from wbportfolio.models.transactions.claim import Claim

    holdings = (
        Claim.get_valid_and_approved_claims(account=account)
        .annotate(year=ExtractYear("date"))
        .values("year", "product")
        .annotate(
            sum_shares=Cast(Sum("shares"), FloatField()),
            product_name=F("product__name"),
            product_isin=F("product__isin"),
        )
        .values("product_name", "product_isin", "sum_shares", "year")
    ).order_by("year", "product")

    return [
        SystemMessage(
            "The following holdings (subscriptions/redemptions) have been found for this account. Please include this data in the analysis and check if there is any correlation between the holding data and the interactions."
        ),
        HumanMessage("List of holdings for the account: {holdings}"),
    ], {"holdings": list(holdings)}
