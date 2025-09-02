from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# from django.utils.translation import gettext_lazy as _
from dynamic_preferences.registries import global_preferences_registry
from wbcore.contrib.authentication.models import User
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.contrib.notifications.utils import create_notification_type

from wbportfolio.models.reconciliations.account_reconciliation_lines import (
    AccountReconciliationLine,
)
from wbportfolio.models.reconciliations.reconciliations import Reconciliation


class AccountReconciliationQuerySet(models.QuerySet):
    def create(self, **kwargs) -> models.QuerySet["AccountReconciliation"]:
        reconciliation = super().create(**kwargs)
        AccountReconciliationLine.objects.update_or_create_for_reconciliation(reconciliation)
        return reconciliation

    def filter_for_user(self, user: User) -> models.QuerySet["AccountReconciliation"]:
        if user.is_superuser or user.is_internal:
            return self

        if not user.has_perm("wbportfolio.view_accountreconciliation"):
            return self.none()

        return self.filter(
            account__roles__role_type__key="reconciliation-manager",
            account__roles__entry_id=user.profile_id,
        )


class AccountReconciliation(Reconciliation):
    lines: models.QuerySet[AccountReconciliationLine]

    account = models.ForeignKey(
        to="wbcrm.Account",
        related_name="wbportfolio_reconciliations",
        on_delete=models.CASCADE,
    )

    objects = AccountReconciliationQuerySet.as_manager()

    class Meta:
        verbose_name = "Account Holdings Reconciliation"
        verbose_name_plural = "Account Holdings Reconciliations"
        constraints = [
            models.UniqueConstraint(fields=["reconciliation_date", "account"], name="unique_date_account"),
        ]
        notification_types = [
            create_notification_type(
                "wbportfolio.account_reconciliation.notify",
                "Account Reconciliation Events",
                "A notification that informs the user about an account reconciliation event.",
                email=True,
                is_lock=True,
            ),
        ]

    def __str__(self) -> str:
        return f"{self.account} ({self.reconciliation_date:%d.%m.%Y})"

    @classmethod
    def get_endpoint_basename(cls):
        return "wbportfolio:accountreconciliation"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbportfolio:accountreconciliationrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{account}} {{reconciliation_date}}"

    def notify(self, update: bool = False, silent_errors: bool = True) -> None:
        registry = global_preferences_registry.manager()
        title = registry["wbportfolio__account_holding_reconciliation_notification_title"]
        body = registry[f"wbportfolio__account_holding_reconciliation_notification_body{'_update' if update else ''}"]
        errors_entries = []
        for role in self.account.roles.filter(role_type__key="reconciliation-manager"):
            try:
                user = User.objects.get(profile_id=role.entry.id)
                send_notification(
                    code="wbportfolio.account_reconciliation.notify",
                    title=title,
                    body=body.format(account=self.account, reconciliation_date=self.reconciliation_date),
                    user=user,
                    reverse_name="wbportfolio:accountreconciliation-detail",
                    reverse_args=[self.id],
                )
            except User.DoesNotExist:
                errors_entries.append(role.entry)
        if errors_entries and not silent_errors:
            raise ValueError(
                f"Because of missing valid user account, we couldn't successfully notify the account holding reconciliation to the following customers:  {', '.join(errors_entries)}. Note: The other customers were successfully notified."
            )


@receiver(post_save, sender=AccountReconciliation)
def notify_on_create(sender, instance: AccountReconciliation, created: bool, **kwargs):
    if created:
        instance.notify()
