from datetime import date, datetime

from django.http import HttpRequest
from django.utils.functional import cached_property

from wbportfolio.models.transactions.claim import Claim


class ClaimPermissionMixin:
    queryset = Claim.objects.all()
    request: HttpRequest

    @cached_property
    def validity_date(self) -> date:
        if validity_date_repr := self.request.GET.get("validity_date"):
            return datetime.strptime(validity_date_repr, "%Y-%m-%d")
        return date.today()

    def get_queryset(self):
        return super().get_queryset().filter_for_user(self.request.user, validity_date=self.validity_date)
