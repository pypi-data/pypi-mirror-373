from datetime import date

from django.db import models

MUTUAL_FUND_TIMEDELTA_DAY_SHIFT = 7


class DataBackendMixin:
    DATE_LABEL = "valuation_date"

    def is_object_valid(self, obj: models.Model) -> bool:
        return super().is_object_valid(obj) and obj.assets.exists() and obj.is_active_at_date(date.today())

    def get_provider_id(self, obj: models.Model) -> str:
        return obj.id
