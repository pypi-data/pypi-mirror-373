import rstr
from faker import Faker
from import_export import fields
from import_export.widgets import ForeignKeyWidget
from wbcore.contrib.io.resources import FilterModelResource
from wbfdm.models import Instrument

from wbportfolio.models import Trade

fake = Faker()


class OrderProposalTradeResource(FilterModelResource):
    """
    Trade Resource class to use to import trade from the order proposal
    """

    DUMMY_FIELD_MAP = {
        "underlying_instrument__isin": lambda: rstr.xeger("([A-Z]{2}[A-Z0-9]{9}[0-9]{1})"),
        "underlying_instrument__ticker": "AAA",
        "underlying_instrument__name": "stock name",
        "weighting": 1.0,
        "shares": 1000.2536,
        "comment": lambda: fake.sentence(),
        "order": 1,
    }
    underlying_instrument__isin = fields.Field(
        column_name="underlying_instrument__isin",
        attribute="underlying_instrument",
        widget=ForeignKeyWidget(Instrument, field="isin"),
    )
    underlying_instrument__name = fields.Field(
        column_name="underlying_instrument__name",
        attribute="underlying_instrument",
        widget=ForeignKeyWidget(Instrument, field="name"),
    )
    underlying_instrument__ticker = fields.Field(
        column_name="underlying_instrument__ticker",
        attribute="underlying_instrument",
        widget=ForeignKeyWidget(Instrument, field="ticker"),
    )

    class Meta:
        fields = (
            "id",
            "underlying_instrument__isin",
            "underlying_instrument__name",
            "underlying_instrument__ticker",
            "weighting",
            "shares",
            "comment",
            "order",
        )
        export_order = fields
        model = Trade
