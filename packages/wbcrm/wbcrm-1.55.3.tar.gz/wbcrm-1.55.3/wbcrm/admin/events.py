from django.contrib import admin

from wbcrm.models.events import Event


@admin.register(Event)
class EventModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "resource",
        "change_type",
        "subject",
        "resource_uuid",
        "action_type",
        "action",
        "created",
        "updated",
    )
    search_fields = ("data", "result")

    @staticmethod
    def change_type(obj):
        return obj.data.get("change_type", "")

    @staticmethod
    def resource(obj):
        return obj.data.get("resource", "")

    @staticmethod
    def subject(obj):
        return obj.data.get("subject", "")

    @staticmethod
    def resource_uuid(obj):
        return obj.data.get("uid", "")

    @staticmethod
    def action_type(obj):
        return obj.result.get("action_type", "")

    @staticmethod
    def action(obj):
        return obj.result.get("action", "")
