from wbcore.contrib.io.backends import AbstractDataBackend, register

from .mixin import DataBackendMixin


@register("Dividend", provider_key="wbfdm", save_data_in_import_source=False, passive_only=False)
class DataBackend(DataBackendMixin, AbstractDataBackend):
    TIMEDELTA = 1
    ATTRIBUTE_NAME = "dividends"
    FILE_NAME = "dividend"
    DEFAULT_MAPPING = {
        "instrument_id": "instrument",
        "rate": "weighting",
        "ex_dividend_date": "value_date",
        "payment_date": "transaction_date",
    }
