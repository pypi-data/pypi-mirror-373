from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import (
    IntegerPreference,
    LongStringPreference,
    StringPreference,
)

portfolio = Section("wbportfolio")
commission = Section("wbcommission")


@global_preferences_registry.register
class TimedeltaImportInstrumentPrice(IntegerPreference):
    section = portfolio
    name = "timedelta_import_instrument_price"
    default = 2

    verbose_name = "The Timedelta for the instrument price import windows"


@global_preferences_registry.register
class DaysToRecomputeRebateFromFeesThreshold(IntegerPreference):
    section = commission
    name = "days_to_recompute_rebate_from_fees_threshold"
    default = 90  # 1 quarter

    verbose_name = "Number of Days to recompute rebate from fees"


@global_preferences_registry.register
class MonthlyNetNewMoneyTarget(IntegerPreference):
    section = portfolio
    name = "monthly_nnm_target"
    default = int(1e6)

    verbose_name = "Monthly Net New Money Target"


@global_preferences_registry.register
class AccountHoldingReconciliationNotificationTitle(StringPreference):
    section = portfolio
    name = "account_holding_reconciliation_notification_title"
    default = "Account Holdings Reconciliation"


@global_preferences_registry.register
class AccountHoldingReconciliationNotificationBody(LongStringPreference):
    section = portfolio
    name = "account_holding_reconciliation_notification_body"
    default = """To validate your holdings, please review the reconciliation for the account {account} on {reconciliation_date}."""


@global_preferences_registry.register
class AccountHoldingReconciliationNotificationBodyUpdate(LongStringPreference):
    section = portfolio
    name = "account_holding_reconciliation_notification_body_update"
    default = """A reconcilation has been updated and requires your review. Please review the reconciliation for the account {account} on {reconciliation_date}."""


@global_preferences_registry.register
class ProductTerminationNoticePeriod(IntegerPreference):
    section = portfolio
    name = "product_termination_notice_period"
    default = 6 * 30  # approx 6 months

    verbose_name = "Product Termination notice period"
