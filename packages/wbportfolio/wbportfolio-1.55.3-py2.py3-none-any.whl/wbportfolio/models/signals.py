from contextlib import suppress

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.dispatch import receiver
from wbfdm.models import Instrument, InstrumentType

from wbportfolio.models import InstrumentPortfolioThroughModel, Product, ProductGroup


def _compute_str(instrument):
    with suppress(ObjectDoesNotExist):
        if instrument.instrument_type == InstrumentType.PRODUCT_GROUP:
            return ProductGroup.objects.get(id=instrument.id).compute_str()
        elif instrument.instrument_type == InstrumentType.PRODUCT:
            return Product.objects.get(id=instrument.id).compute_str()
    return instrument.get_compute_str()


@receiver(models.signals.class_prepared)
def add_to_instrument(sender, **kwargs):
    Instrument.add_to_class("portfolio", property(InstrumentPortfolioThroughModel.get_portfolio))
    Instrument.add_to_class("primary_portfolio", property(InstrumentPortfolioThroughModel.get_primary_portfolio))
    Instrument.add_to_class("compute_str", _compute_str)
