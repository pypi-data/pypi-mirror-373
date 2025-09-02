import re

from wbcore.contrib.currency.models import Currency
from wbcore.contrib.directory.models import Company


def get_currency_and_assets_under_management(
    aum_string, currency_mapping, default_currency, multiplier_mapping, default_multiplier
):
    currency = default_currency
    multiplier = default_multiplier

    regex_number = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", aum_string)

    if regex_number:
        regex_number = regex_number[0]
    else:
        return None, None

    aum_string = aum_string.lower()

    for mapping in currency_mapping.keys():
        if mapping in aum_string:
            currency = currency_mapping[mapping]
            aum_string = aum_string.replace(mapping, "")

    for mapping in multiplier_mapping.keys():
        if mapping in aum_string:
            multiplier = multiplier_mapping[mapping]
            aum_string = aum_string.replace(mapping, "")

    return float(regex_number) * multiplier, currency


def assign_aum():
    default_currency = Currency.objects.get(key="USD")

    currency_mapping = {
        "chf": Currency.objects.get(key="CHF"),
        "eur": Currency.objects.get(key="EUR"),
        "€": Currency.objects.get(key="EUR"),
        "usd": Currency.objects.get(key="USD"),
        "$": Currency.objects.get(key="USD"),
    }

    multiplier_mapping = {
        "billion": 1000000000,
        "bn": 1000000000,
        "b.": 1000000000,
        "b": 1000000000,
        "million": 1000000,
        "mio": 1000000,
        "mm": 1000000,
        "mn": 1000000,
        "m": 1000000,
    }

    for company in Company.objects.all():
        assets_under_management, currency = get_currency_and_assets_under_management(
            aum_string=company.assets_under_management,
            currency_mapping=currency_mapping,
            default_currency=default_currency,
            multiplier_mapping=multiplier_mapping,
            default_multiplier=1000000,
        )

        if not hasattr(company, "portfolio_data"):
            company.save()

        portfolio_data = company.portfolio_data
        portfolio_data.assets_under_management = assets_under_management
        portfolio_data.assets_under_management_currency = currency
        try:
            portfolio_data.save()
        except Exception:
            pass
