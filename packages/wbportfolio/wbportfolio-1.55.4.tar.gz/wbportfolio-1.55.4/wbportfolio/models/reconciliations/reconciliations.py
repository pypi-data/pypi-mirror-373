from django.db import models
from django.utils.translation import gettext_lazy as _
from wbcore.models import WBModel


class Reconciliation(WBModel):
    reconciliation_date = models.DateField()

    creator = models.ForeignKey(
        to="authentication.User",
        on_delete=models.PROTECT,
        related_name="+",
    )
    approved_by = models.ForeignKey(
        to="authentication.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
        related_name="+",
    )
    approved_dt = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved Timestamp"))

    class Meta:
        abstract = True
