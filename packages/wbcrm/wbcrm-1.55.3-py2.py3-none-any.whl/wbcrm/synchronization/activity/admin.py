from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from wbcore.contrib.authentication.admin import UserAdmin

from wbcrm.admin import ActivityAdmin
from wbcrm.models import Activity

from .shortcuts import get_backend

User = get_user_model()
admin.site.unregister(User)
admin.site.unregister(Activity)


@admin.register(Activity)
class ActivitySyncAdmin(ActivityAdmin):
    def delete_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        for obj in queryset.filter(is_active=True):
            obj.delete()
        super().delete_queryset(request, queryset)


@admin.register(User)
class UserSyncAdmin(UserAdmin):
    def set_web_hook(self, request, queryset):
        try:
            if controller := get_backend():
                for user in queryset:
                    controller.backend.set_web_hook(user)
                self.message_user(
                    request,
                    _("Operation completed, we have set the webhook for {} users.").format(queryset.count()),
                )
            else:
                raise ValueError("No backend set in preferences")
        except Exception as e:
            self.message_user(request, _("Operation Failed, {}").format(e), messages.WARNING)

    def stop_web_hook(self, request, queryset):
        try:
            if controller := get_backend():
                for user in queryset:
                    controller.backend.stop_web_hook(user)
                self.message_user(
                    request,
                    _("Operation completed, we have stopped the webhook for {} users.").format(queryset.count()),
                )
            else:
                raise ValueError("No backend set in preferences")
        except Exception as e:
            self.message_user(request, _("Operation Failed, {}").format(e), messages.WARNING)

    def check_web_hook(self, request, queryset):
        try:
            if controller := get_backend():
                for user in queryset:
                    controller.backend.check_web_hook(user)
                self.message_user(
                    request,
                    _("Operation completed, we checked the webhook for {} users.").format(queryset.count()),
                )
            else:
                raise ValueError("No backend set in preferences")
        except Exception as e:
            self.message_user(request, _("Operation Failed, {}").format(e), messages.WARNING)

    actions = UserAdmin.actions + (
        set_web_hook,
        stop_web_hook,
        check_web_hook,
    )
