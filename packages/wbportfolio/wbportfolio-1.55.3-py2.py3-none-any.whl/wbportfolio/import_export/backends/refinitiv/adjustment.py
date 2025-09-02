from datetime import datetime
from io import BytesIO
from typing import Optional

from django.db import models
from pandas.tseries.offsets import BDay
from wbcore.contrib.io.backends import AbstractDataBackend, register
from wbfdm.import_export.backends.refinitiv.utils import Controller
from wbportfolio.import_export.backends.utils import (
    get_timedelta_import_instrument_price,
)

from ..wbfdm.mixin import DataBackendMixin

DEFAULT_MAPPING = {"AX": "factor"}


@register("Adjustment", provider_key="refinitiv")
class DataBackend(DataBackendMixin, AbstractDataBackend):
    CHUNK_SIZE = 50

    def __init__(self, import_credential: Optional[models.Model] = None, **kwargs):
        self.controller = Controller(import_credential.username, import_credential.password)

    def get_files(
        self,
        execution_time: datetime,
        obj_external_ids: list[str] = None,
        **kwargs,
    ) -> BytesIO:
        execution_date = execution_time.date()
        start = kwargs.get("start", (execution_date - BDay(get_timedelta_import_instrument_price())).date())
        fields = list(DEFAULT_MAPPING.keys())
        if obj_external_ids:
            df = self.controller.get_data(obj_external_ids, fields, start, execution_date)
            if not df.empty:
                content_file = BytesIO()
                df.to_json(content_file, orient="records")
                file_name = f"adjustment_chunk-{start:%Y-%m-%d}-{execution_date:%Y-%m-%d}_{datetime.timestamp(execution_time)}.json"
                yield file_name, content_file
