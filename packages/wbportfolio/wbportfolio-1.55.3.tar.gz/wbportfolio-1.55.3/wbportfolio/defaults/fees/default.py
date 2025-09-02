from wbfdm.models import InstrumentPrice

from wbportfolio.models import FeeProductPercentage, Fees, Product


def fees_calculation(price_id):
    price = InstrumentPrice.objects.get(id=price_id)
    if price.calculated:
        raise ValueError("Cannot compute fees on calculated price")
    currency = price.instrument.currency
    product = Product.objects.get(id=price.instrument.id)
    portfolio = product.portfolio
    previous_price = price.previous_price

    if previous_price:
        shares = product.total_shares(previous_price.date)
        multiplicator = shares * previous_price.net_value
    else:
        shares = product.total_shares(price.date)
        multiplicator = shares * product.share_price

    product_net_management_fees = product.get_fees_percent(price.date, FeeProductPercentage.Type.MANAGEMENT)
    product_net_performance_fees = product.get_fees_percent(price.date, FeeProductPercentage.Type.PERFORMANCE)
    product_gross_performance_fees = product.get_fees_percent(
        price.date, FeeProductPercentage.Type.PERFORMANCE, net=False
    )

    if previous_price and previous_price.date.weekday() == 4:
        # The previous InstrumentPrice was a Friday. This means we have to calculate for the weekend
        previous_total_value = shares * previous_price.net_value

        sat_bank_fees = (product.bank_fees / 360) * previous_total_value
        sat_management_fees = (product_net_management_fees / 360) * previous_total_value
        previous_total_value = previous_total_value - sat_bank_fees - sat_management_fees

        sun_bank_fees = (product.bank_fees / 360) * previous_total_value
        sun_management_fees = (product_net_management_fees / 360) * previous_total_value
        previous_total_value = previous_total_value - sun_bank_fees - sun_management_fees

        mon_bank_fees = (product.bank_fees / 360) * previous_total_value
        mon_management_fees = (product_net_management_fees / 360) * previous_total_value
        bank_fees = sat_bank_fees + sun_bank_fees + mon_bank_fees
        management_fees = sat_management_fees + sun_management_fees + mon_management_fees
    else:
        bank_fees = (product.bank_fees / 360) * multiplicator
        management_fees = (product_net_management_fees / 360) * multiplicator

    value = (
        price.net_value or price.gross_value
    )  # Flipped around, so that if we have a good net price from the bank, we rather use that one. Issue is, that if the gross price is completely off, the performance fees can be really really high.
    multiplicator = max(0, value - product.get_high_water_mark(price.date)) * shares
    performance_fees_net = product_net_performance_fees * multiplicator
    performance_fees_gross = product_gross_performance_fees * multiplicator
    base_fields = [
        "total_value",
        "total_value_gross",
    ]
    yield {
        "portfolio": portfolio,
        "product": product,
        "fee_date": price.date,
        "transaction_subtype": Fees.Type.MANAGEMENT,
        "currency": currency,
        "calculated": True,
        **{f: management_fees for f in base_fields},
    }
    yield {
        "portfolio": portfolio,
        "product": product,
        "fee_date": price.date,
        "transaction_subtype": Fees.Type.ISSUER,
        "currency": currency,
        "calculated": True,
        **{f: bank_fees for f in base_fields},
    }
    yield {
        "portfolio": portfolio,
        "product": product,
        "fee_date": price.date,
        "transaction_subtype": Fees.Type.PERFORMANCE,
        "currency": currency,
        "calculated": True,
        "total_value": performance_fees_net,
        "total_value_gross": performance_fees_gross,
    }
