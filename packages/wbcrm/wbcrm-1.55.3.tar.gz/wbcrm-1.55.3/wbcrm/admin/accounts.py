from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from wbcrm.models.accounts import (
    Account,
    AccountRole,
    AccountRoleType,
    AccountRoleValidity,
)


class AccountRoleValidityTabularInline(admin.TabularInline):
    model = AccountRoleValidity
    fields = ("timespan",)
    extra = 0


class AccountRoleTabularInline(admin.TabularInline):
    model = AccountRole
    fields = ("role_type", "entry", "weighting", "is_hidden")
    autocomplete_fields = ["entry", "account"]
    extra = 0
    show_change_link = True


class AccountTabularInline(admin.TabularInline):
    model = Account
    fields = ("title", "status", "owner", "is_terminal_account", "is_active", "is_public")
    autocomplete_fields = ["owner", "parent"]
    fk_name = "parent"
    show_change_link = True
    extra = 0


@admin.register(AccountRoleType)
class AccountRoleTypeModelAdmin(admin.ModelAdmin):
    list_display = ("title", "key")
    search_fields = ("title", "key")


@admin.register(AccountRole)
class AccountRoleModelAdmin(admin.ModelAdmin):
    list_display = ("role_type", "entry", "account", "is_hidden")
    inlines = [AccountRoleValidityTabularInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("entry", "account")


@admin.register(Account)
class AccountModelAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    fsm_field = ["status"]
    search_fields = ["title"]
    list_display = ["computed_str", "status", "is_active", "is_terminal_account", "is_public", "owner"]
    inlines = [AccountRoleTabularInline, AccountTabularInline]
    autocomplete_fields = ["owner", "parent"]

    def get_queryset(self, request):
        return Account.all_objects.select_related("owner", "parent")
