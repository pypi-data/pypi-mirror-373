from django.contrib import admin

from wbportfolio.models import InstrumentPortfolioThroughModel
from wbportfolio.models.portfolio_relationship import (
    PortfolioInstrumentPreferredClassificationThroughModel,
)


class PortfolioInstrumentPreferredClassificationThroughInlineModelAdmin(admin.TabularInline):
    model = PortfolioInstrumentPreferredClassificationThroughModel
    fk_name = "portfolio"
    raw_id_fields = [
        "portfolio",
        "instrument",
        "classification",
        "classification_group",
    ]


class InstrumentPortfolioThroughModelAdmin(admin.TabularInline):
    model = InstrumentPortfolioThroughModel
    fk_name = "instrument"
    autocomplete_fields = ["portfolio"]
