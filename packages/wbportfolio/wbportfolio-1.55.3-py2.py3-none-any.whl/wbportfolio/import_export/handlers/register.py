from datetime import datetime
from typing import Any, Dict, Optional

from django.db import models
from wbcore.contrib.geography.models import Geography
from wbcore.contrib.io.imports import ImportExportHandler


class RegisterImportHandler(ImportExportHandler):
    MODEL_APP_LABEL = "wbportfolio.Register"

    def _deserialize(self, data: Dict[str, Any]):
        if "opened" in data:
            data["opened"] = datetime.strptime(data["opened"], "%Y-%m-%d").date()
        if residence_id := data.get("residence"):
            data["residence"] = Geography.countries.get(id=residence_id)
        if citizenship_id := data.get("citizenship"):
            data["citizenship"] = Geography.countries.get(id=citizenship_id)
        if outlet_country_id := data.get("outlet_country"):
            data["outlet_country"] = Geography.countries.get(id=outlet_country_id)
        if custodian_country_id := data.get("custodian_country"):
            data["custodian_country"] = Geography.countries.get(id=custodian_country_id)

        outlet_city = data.pop("outlet_city", None)
        if (outlet_country := data.get("outlet_country", None)) and outlet_city:
            if res := outlet_country.lookup_descendants(outlet_city, level=Geography.Level.CITY.value):
                data["outlet_city"] = res

        custodian_city = data.pop("custodian_city", None)
        if (custodian_country := data.get("custodian_country", None)) and custodian_city:
            if res := custodian_country.lookup_descendants(custodian_city, level=Geography.Level.CITY.value):
                data["custodian_city"] = res

    def _get_instance(self, data: Dict[str, Any], history: Optional[models.QuerySet] = None, **kwargs) -> models.Model:
        self.import_source.log += "Get Register Instance."
        self.import_source.log += f"Parameter: Reference={data['register_reference']}"
        if isinstance(data, int):
            return self.model.objects.get(id=data)
        return self.model.objects.filter(register_reference=data["register_reference"]).first()

    def _create_instance(self, data: Dict[str, Any], **kwargs) -> models.Model:
        self.import_source.log += "Create Register."
        return self.model.objects.create(import_source=self.import_source, **data)
