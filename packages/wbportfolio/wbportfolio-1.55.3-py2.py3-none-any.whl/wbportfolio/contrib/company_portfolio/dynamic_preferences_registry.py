from contextlib import suppress

from django.db.utils import ProgrammingError
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from wbcore.contrib.directory.models import CustomerStatus
from wbcore.contrib.dynamic_preferences.types import (
    CallableDefaultModelChoicePreference,
)

portfolio = Section("wbportfolio")


def get_default_returning_client_customer_status():
    with suppress(ProgrammingError):
        return CustomerStatus.objects.filter(title="Returning Client").first()


def get_default_lost_client_customer_status():
    with suppress(ProgrammingError):
        return CustomerStatus.objects.filter(title="Lost Client").first()


def get_default_tpm_customer_status():
    with suppress(ProgrammingError):
        return CustomerStatus.objects.filter(title="Third Party Marketer (TPM)").first()


def get_default_client_customer_status():
    with suppress(ProgrammingError):
        return CustomerStatus.objects.filter(title="Client").first()


@global_preferences_registry.register
class ReturningClientCustomerStatus(CallableDefaultModelChoicePreference):
    section = portfolio
    name = "returning_client_customer_status"
    model = CustomerStatus

    verbose_name = "Returning Client customer status"
    help_text = "The customer status corresponding to the Returning Client Group"

    @property
    def default(self):
        return get_default_returning_client_customer_status()


@global_preferences_registry.register
class LostClientCustomerStatus(CallableDefaultModelChoicePreference):
    section = portfolio
    name = "lost_client_customer_status"
    model = CustomerStatus

    verbose_name = "Lost Client customer status"
    help_text = "The customer status corresponding to the Lost Client Group"

    @property
    def default(self):
        return get_default_lost_client_customer_status()


@global_preferences_registry.register
class TPMCustomerStatus(CallableDefaultModelChoicePreference):
    section = portfolio
    name = "tpm_customer_status"
    model = CustomerStatus

    verbose_name = "TPM customer status"
    help_text = "The customer status corresponding to the TPM group"

    @property
    def default(self):
        return get_default_tpm_customer_status()


@global_preferences_registry.register
class ClientCustomerStatus(CallableDefaultModelChoicePreference):
    section = portfolio
    name = "client_customer_status"
    model = CustomerStatus

    verbose_name = "Client customer status"
    help_text = "The customer status corresponding to the Client group"

    @property
    def default(self):
        return get_default_client_customer_status()
