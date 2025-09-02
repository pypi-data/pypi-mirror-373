from django.contrib import admin

from wbportfolio.models import AccountReconciliation, AccountReconciliationLine


class AccountReconciliationLineInline(admin.TabularInline):
    model = AccountReconciliationLine
    fields = ("product", "price", "price_date", "shares", "shares_external")
    extra = 0


@admin.register(AccountReconciliation)
class AccountReconciliationAdmin(admin.ModelAdmin):
    list_display = ("reconciliation_date", "account", "creator")
    inlines = [AccountReconciliationLineInline]
