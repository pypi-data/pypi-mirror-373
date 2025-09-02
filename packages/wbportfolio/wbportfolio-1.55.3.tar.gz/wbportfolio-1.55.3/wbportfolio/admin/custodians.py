from django.contrib import admin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from wbportfolio.models import Custodian


@admin.register(Custodian)
class CustodianModelAdmin(admin.ModelAdmin, DynamicArrayMixin):
    search_fields = ("name", "mapping")
    list_display = ("name", "mapping", "company")
