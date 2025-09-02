from django.contrib import admin

from wbportfolio.models import Register


@admin.register(Register)
class RegisterModelAdmin(admin.ModelAdmin):
    search_fields = [
        "register_reference",
        "register_name_1",
        "register_name_2",
        "custodian_reference",
        "custodian_name_1",
        "custodian_name_2",
        "outlet_reference",
        "outlet_name",
    ]
    list_display = ("register_reference", "global_register_reference", "register_name_1", "register_name_2")
