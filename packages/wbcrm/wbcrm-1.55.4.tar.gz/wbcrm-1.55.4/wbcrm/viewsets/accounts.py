from django.db.models import Case, Exists, F, IntegerField, OuterRef, When
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework.exceptions import AuthenticationFailed
from wbcore import viewsets
from wbcore.utils.views import MergeMixin

from wbcrm.filters import AccountFilter, AccountRoleFilterSet
from wbcrm.models.accounts import Account, AccountRole, AccountRoleType
from wbcrm.serializers.accounts import (
    AccountModelSerializer,
    AccountRepresentationSerializer,
    AccountRoleModelSerializer,
    AccountRoleTypeRepresentationSerializer,
)
from wbcrm.viewsets.buttons import AccountButtonConfig
from wbcrm.viewsets.display import (
    AccountDisplayConfig,
    AccountRoleAccountDisplayConfig,
    InheritedAccountRoleAccountDisplayConfig,
)
from wbcrm.viewsets.endpoints import (
    AccountRoleAccountEndpointConfig,
    ChildAccountAccountEndpointConfig,
    InheritedAccountRoleAccountEndpointConfig,
)
from wbcrm.viewsets.titles import (
    AccountRoleAccountTitleConfig,
    AccountTitleConfig,
    ChildAccountAccountTitleConfig,
)

from .mixins import AccountPermissionMixin, AccountRolePermissionMixin


class AccountRoleTypeRepresentationViewSet(viewsets.RepresentationViewSet):
    ordering_fields = search_fields = ordering = ("title",)
    serializer_class = AccountRoleTypeRepresentationSerializer
    queryset = AccountRoleType.objects.all()


class AccountRepresentationViewSet(AccountPermissionMixin, viewsets.RepresentationViewSet):
    ordering_fields = ("title",)
    search_fields = ["computed_str", "owner__computed_str"]
    filterset_class = AccountFilter

    serializer_class = AccountRepresentationSerializer
    queryset = Account.all_objects.all()
    ordering = ["title"]


class AccountModelViewSet(MergeMixin, AccountPermissionMixin, viewsets.ModelViewSet):
    serializer_class = AccountModelSerializer
    filterset_class = AccountFilter
    queryset = Account.all_objects.select_related("owner", "parent").annotate(
        has_children=Exists(Account.objects.filter(parent=OuterRef("pk"))),
        _group_key=Case(When(has_children=True, then=F("id")), default=None, output_field=IntegerField()),
    )

    ordering = ordering_fields = [
        "title",
        "owner__computed_str",
        "reference_id",
        "is_terminal_account",
        "is_public",
        "is_active",
    ]
    search_fields = ["computed_str", "owner__computed_str"]

    display_config_class = AccountDisplayConfig
    title_config_class = AccountTitleConfig
    button_config_class = AccountButtonConfig

    def get_merged_object_representation_serializer(self):
        return AccountRepresentationSerializer


class ChildAccountAccountModelViewSet(AccountModelViewSet):
    title_config_class = ChildAccountAccountTitleConfig
    endpoint_config_class = ChildAccountAccountEndpointConfig

    def dispatch(self, *args, **kwargs):
        kwargs["parent_id"] = kwargs.get("account_id", None)
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(parent_id=self.kwargs["account_id"])


class AccountRoleAccountModelViewSet(AccountRolePermissionMixin, viewsets.ModelViewSet):
    display_config_class = AccountRoleAccountDisplayConfig
    title_config_class = AccountRoleAccountTitleConfig
    endpoint_config_class = AccountRoleAccountEndpointConfig
    serializer_class = AccountRoleModelSerializer

    filterset_class = AccountRoleFilterSet
    queryset = AccountRole.objects.select_related(
        "entry",
        "account",
    )
    ordering = ["role_type", "id"]

    @cached_property
    def account(self):
        account = get_object_or_404(Account, pk=self.kwargs["account_id"])
        if not account.can_see_account(self.request.user):
            raise AuthenticationFailed()
        return account

    def get_queryset(self):
        return super().get_queryset().filter(account=self.account)


class InheritedAccountRoleAccountModelViewSet(AccountRoleAccountModelViewSet):
    display_config_class = InheritedAccountRoleAccountDisplayConfig
    endpoint_config_class = InheritedAccountRoleAccountEndpointConfig
    READ_ONLY = True

    def get_queryset(self):
        return AccountRole.objects.filter(
            id__in=self.account.get_inherited_roles_for_account().values("id")
        ).filter_for_user(self.request.user, validity_date=self.validity_date)
