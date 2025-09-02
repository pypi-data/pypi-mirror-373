from datetime import date

from django.utils.functional import cached_property

from wbcrm.models.accounts import Account, AccountRole


class AccountPermissionMixin:
    queryset = Account.objects.all()

    @cached_property
    def validity_date(self) -> date:
        if validity_date_repr := self.request.GET.get("validity_date"):
            return date.strftime(validity_date_repr, "%Y-%m-%d")
        return date.today()

    def get_queryset(self, *args, **kwargs):
        return (
            super().get_queryset(*args, **kwargs).filter_for_user(self.request.user, validity_date=self.validity_date)
        )


class AccountRolePermissionMixin:
    queryset = AccountRole.objects.all()

    @cached_property
    def validity_date(self) -> date:
        if validity_date_repr := self.request.GET.get("validity_date"):
            return date.strftime(validity_date_repr, "%Y-%m-%d")
        return date.today()

    def get_queryset(self, *args, **kwargs):
        return (
            super().get_queryset(*args, **kwargs).filter_for_user(self.request.user, validity_date=self.validity_date)
        )
