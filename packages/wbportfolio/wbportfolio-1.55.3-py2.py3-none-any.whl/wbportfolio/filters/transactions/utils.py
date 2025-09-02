from datetime import date, timedelta

from psycopg.types.range import DateRange

from wbportfolio.models import Fees, Trade


def get_transaction_gte_default(field, request, view):
    filter_date = date.today() - timedelta(days=90)
    qs = Trade.objects.none()
    if "instrument_id" in view.kwargs:
        qs = Trade.objects.filter(underlying_instrument__id=view.kwargs["instrument_id"])
    elif "portfolio_id" in view.kwargs:
        qs = Trade.objects.filter(portfolio__id=view.kwargs["portfolio_id"])
    if qs.exists():
        filter_date = qs.earliest("transaction_date").transaction_date
    return filter_date


def get_transaction_underlying_type_choices(*args):
    models = [Fees, Trade]
    choices = []
    for model in models:
        for choice in model.Type.choices:
            choices.append(choice)
    return choices


def get_transaction_lte_default(field, request, view):
    filter_date = date.today() + timedelta(days=7)
    qs = Trade.objects.none()
    if "instrument_id" in view.kwargs:
        qs = Trade.objects.filter(underlying_instrument__id=view.kwargs["instrument_id"])
    elif "portfolio_id" in view.kwargs:
        qs = Trade.objects.filter(portfolio__id=view.kwargs["portfolio_id"])
    if qs.exists():
        filter_date = qs.latest("transaction_date").transaction_date
    return filter_date


def get_transaction_default_date_range(*args, **kwargs):
    return DateRange(get_transaction_gte_default(*args, **kwargs), get_transaction_lte_default(*args, **kwargs))
