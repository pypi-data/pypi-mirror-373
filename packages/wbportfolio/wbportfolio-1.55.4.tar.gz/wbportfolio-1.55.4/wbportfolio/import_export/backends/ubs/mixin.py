from datetime import date

from django.db import models

from wbportfolio.models.products import Product


class DataBackendMixin:
    def is_object_valid(self, obj: models.Model) -> bool:
        return super().is_object_valid(obj) and obj.is_active_at_date(date.today()) and obj.isin

    def get_default_queryset(self):
        return Product.objects.filter(bank=self.ubs_bank, isin__isnull=False)

    def get_provider_id(self, obj: models.Model) -> str:
        return obj.isin
