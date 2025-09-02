import json
from datetime import datetime
from io import BytesIO

from django.core.serializers.json import DjangoJSONEncoder
from pandas.tseries.offsets import BDay
from wbcore.contrib.io.backends import AbstractDataBackend, register
from wbfdm.models import Instrument

from wbportfolio.import_export.backends.utils import (
    get_timedelta_import_instrument_price,
)

from .mixin import DataBackendMixin


@register("Adjustment", provider_key="wbfdm", save_data_in_import_source=False, passive_only=False)
class DataBackend(DataBackendMixin, AbstractDataBackend):
    DATE_LABEL = "adjustment_date"
    DEFAULT_MAPPING = {
        "adjustment_date": "date",
        "adjustment_factor": "factor",
        "cumulative_adjustment_factor": "cumulative_factor",
        "instrument_id": "instrument",
    }
    NONE_NULLABLE_FIELDS = list(DEFAULT_MAPPING.values())

    def get_default_queryset(self):
        return Instrument.objects.filter(is_investable_universe=True)

    def get_files(
        self,
        execution_time: datetime,
        **kwargs,
    ) -> BytesIO:
        execution_date = execution_time.date()
        start = kwargs.get("start", (execution_date - BDay(get_timedelta_import_instrument_price())).date())
        data = []
        for dict_dto in self.get_default_queryset().dl.adjustments(
            from_date=start,
            to_date=execution_date,
        ):
            if dict_dto["adjustment_factor"] is not None:
                data.append(dict_dto)
        if data:
            content_file = BytesIO()
            content_file.write(json.dumps(data, cls=DjangoJSONEncoder).encode())
            file_name = (
                f"adjustment_{start:%Y-%m-%d}-{execution_date:%Y-%m-%d}_{datetime.timestamp(execution_time)}.json"
            )
            yield file_name, content_file
