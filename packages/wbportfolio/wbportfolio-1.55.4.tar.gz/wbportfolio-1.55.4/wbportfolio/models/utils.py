from wbfdm.models import Instrument

from wbportfolio.models import Index, Product


def get_casted_portfolio_instrument(instrument: Instrument) -> Product | Index | None:
    try:
        return Product.objects.get(id=instrument.id)
    except Product.DoesNotExist:
        try:
            return Index.objects.get(id=instrument.id)
        except Index.DoesNotExist:
            return None
