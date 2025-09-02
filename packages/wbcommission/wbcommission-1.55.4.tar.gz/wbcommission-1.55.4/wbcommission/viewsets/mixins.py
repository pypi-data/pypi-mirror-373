from datetime import date, datetime

from django.http import HttpRequest
from django.utils.functional import cached_property

from wbcommission.models import Commission, Rebate


class CommissionPermissionMixin:
    queryset = Commission.objects.all()
    request: HttpRequest

    @cached_property
    def validity_date(self) -> date:
        if validity_date_repr := self.request.GET.get("validity_date"):
            return datetime.strptime(validity_date_repr, "%Y-%m-%d")
        return date.today()

    def get_queryset(self):
        # allow the user to see claim only on accounts it can see
        return (
            super().get_queryset().filter_for_user(self.request.user, validity_date=self.validity_date)  # type: ignore
        )


class RebatePermissionMixin:
    queryset = Rebate.objects.all()
    request: HttpRequest

    @cached_property
    def validity_date(self) -> date:
        if validity_date_repr := self.request.GET.get("validity_date"):
            return datetime.strptime(validity_date_repr, "%Y-%m-%d")
        return date.today()

    def get_queryset(self):
        # allow the user to see claim only on accounts it can see
        return (
            super().get_queryset().filter_for_user(self.request.user, validity_date=self.validity_date)  # type: ignore
        )
