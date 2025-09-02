import json
from datetime import date, datetime
from io import BytesIO
from typing import Optional

from django.db import models
from pandas.tseries.offsets import BDay
from wbcore.contrib.io.backends import AbstractDataBackend, register

from wbportfolio.api_clients.ubs import UBSNeoAPIClient

from .mixin import DataBackendMixin


@register("Asset Position", provider_key="ubs", save_data_in_import_source=True, passive_only=True)
class DataBackend(DataBackendMixin, AbstractDataBackend):
    def __init__(
        self, import_credential: Optional[models.Model] = None, ubs_bank: Optional[models.Model] = None, **kwargs
    ):
        if not ubs_bank:
            raise ValueError("The ubs company objects needs to be passed to this backend")
        self.ubs_bank = ubs_bank
        if not import_credential or not import_credential.authentication_token:
            raise ValueError("UBS backend needs a valid import credential object")
        self.authentication_token = import_credential.authentication_token.replace("Bearer ", "")
        self.token_expiry_date = import_credential.validity_end

    def get_files(
        self,
        execution_time: datetime,
        start: date = None,
        obj_external_ids: list[str] = None,
        **kwargs,
    ) -> BytesIO:
        execution_date = (execution_time - BDay(1)).date()
        if obj_external_ids:
            client = UBSNeoAPIClient(self.authentication_token, self.token_expiry_date)
            for external_id in obj_external_ids:
                res_json = client.validate_response(client.get_portfolio_at_date(external_id, execution_date))
                if res_json:
                    content_file = BytesIO()
                    content_file.write(json.dumps(res_json).encode())
                    file_name = f"ubs_positions_{external_id}_{execution_date:%Y-%m-%d}_{datetime.timestamp(execution_time)}.json"
                    yield file_name, content_file
