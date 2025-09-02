from django.apps import apps
from django.contrib.messages import warning
from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueValidator
from wbcore import serializers as wb_serializers
from wbcore.contrib.authentication.models import User
from wbcore.contrib.authentication.serializers import UserRepresentationSerializer
from wbcore.contrib.directory.serializers import EntryRepresentationSerializer

from wbcrm.models.accounts import Account, AccountRole, AccountRoleType


class AccountRoleTypeRepresentationSerializer(wb_serializers.RepresentationSerializer):
    class Meta:
        model = AccountRoleType
        fields = ("id", "title")


class AccountRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbcrm:account-detail")

    def get_filter_params(self, request):
        return {"is_active": True}

    class Meta:
        model = Account
        fields = ("id", "computed_str", "_detail")


class TerminalAccountRepresentationSerializer(AccountRepresentationSerializer):
    def get_filter_params(self, request):
        filter_params = {"is_terminal_account": True, "status": "OPEN", "is_active": True}
        if view := request.parser_context.get("view", None):
            if entry_id := view.kwargs.get("entry_id", None):
                filter_params["customer"] = entry_id
            if account_id := view.kwargs.get("account_id", None):
                filter_params["account"] = account_id
        return filter_params


class AccountModelSerializer(wb_serializers.ModelSerializer):
    _parent = AccountRepresentationSerializer(source="parent")
    _owner = EntryRepresentationSerializer(source="owner")
    _group_key = wb_serializers.CharField(read_only=True)
    reference_id = wb_serializers.IntegerField(
        label="Reference ID",
        default=lambda: Account.get_next_available_reference_id(),
        read_only=lambda view: not view.new_mode,
        validators=[UniqueValidator(queryset=Account.objects.all())],
    )

    @wb_serializers.register_resource()
    def additional_resources(self, instance, request, user):
        request = self.context["request"]

        custom_buttons = {
            "childaccounts": reverse("wbcrm:account-childaccount-list", args=[instance.id], request=request),
            "accountroles": reverse("wbcrm:account-accountrole-list", args=[instance.id], request=request),
            "inheritedaccountroles": reverse("wbcrm:account-inheritedrole-list", args=[instance.id], request=request),
        }
        if apps.is_installed("wbportfolio"):  # TODO move as signal
            custom_buttons["claims"] = reverse("wbportfolio:account-claim-list", args=[instance.id], request=request)

        return custom_buttons

    relationship_status = wb_serializers.RangeSelectField(
        color="rgb(220,20,60)",
        label="Relationship Status",
        start=1,
        end=5,
        step_size=1,
        read_only=True,
        required=False,
    )

    class Meta:
        model = Account
        fields = (
            "id",
            "_group_key",
            "title",
            "status",
            "is_active",
            "is_terminal_account",
            "is_public",
            "_parent",
            "parent",
            "_owner",
            "owner",
            "reference_id",
            "computed_str",
            "relationship_status",
            "relationship_summary",
            "action_plan",
            "_additional_resources",
        )


class AccountRoleModelSerializer(wb_serializers.ModelSerializer):
    _entry = EntryRepresentationSerializer(source="entry")
    _account = AccountRepresentationSerializer(source="account")
    _role_type = AccountRoleTypeRepresentationSerializer(source="role_type")
    is_currently_valid = wb_serializers.BooleanField(read_only=True, default=False)

    _authorized_hidden_users = UserRepresentationSerializer(source="authorized_hidden_users", many=True)

    def create(self, validated_data):
        # We return a get or create role because we don't want to leak information on already existing role that the user might not be able to see
        # this way, the account role (even if already existing) will be returned and the permission mixin will take over
        authorized_hidden_users = validated_data.pop("authorized_hidden_users", [])
        instance, created = AccountRole.objects.get_or_create(
            entry=validated_data.pop("entry"), account=validated_data.pop("account"), defaults=validated_data
        )
        if authorized_hidden_users:
            instance.authorized_hidden_users.set(authorized_hidden_users)
        if request := self.context.get("request"):
            if not User.objects.filter(profile_id=instance.entry.id).exists():
                warning(
                    request,
                    _(
                        "The selected entry does not have an associated user account. Note: Notifications cannot be sent to users without an account."
                    ),
                )
        return instance

    class Meta:
        model = AccountRole
        fields = (
            "id",
            "role_type",
            "_role_type",
            "entry",
            "_entry",
            "account",
            "_account",
            "is_currently_valid",
            "is_hidden",
            "authorized_hidden_users",
            "_authorized_hidden_users",
        )
