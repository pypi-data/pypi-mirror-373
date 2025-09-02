from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from wbcrm.models import Activity, ActivityParticipant, ActivityType
from wbcrm.models.activities import ActivityCompanyThroughModel


class ParticipantInline(admin.TabularInline):
    model = ActivityParticipant


class CompanyInline(admin.TabularInline):
    model = ActivityCompanyThroughModel


@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    search_fields = ("title",)
    list_display = ("id", "title")


class ActivityInline(admin.StackedInline):
    model = Activity
    fk_name = "parent_occurrence"
    extra = 0
    fieldsets = (
        (
            _("Main information"),
            {
                "fields": (
                    "title",
                    "description",
                )
            },
        ),
    )


@admin.register(Activity)
class ActivityAdmin(VersionAdmin):
    search_fields = ("title",)
    list_display = ("id", "status", "title", "period", "is_active", "parent_occurrence_id", "metadata")
    fieldsets = (
        (_("Main information"), {"fields": ("title", "description", "result", "creator")}),
        (_("Meta"), {"fields": ("status", "type", "visibility", "is_active", "metadata")}),
        (_("Temporal Information"), {"fields": ("period", "all_day")}),
        (_("Geographical Information"), {"fields": ("location", "location_longitude", "location_latitude")}),
        (_("Linked Entries"), {"fields": ("assigned_to", "groups")}),
        (_("Linked Activities"), {"fields": ("preceded_by",)}),
        (_("LLM"), {"fields": ("heat", "summary")}),
        (
            _("Recurrence"),
            {
                "fields": (
                    "repeat_choice",
                    "parent_occurrence",
                    ("recurrence_count", "recurrence_end"),
                    "propagate_for_all_children",
                )
            },
        ),
    )

    raw_id_fields = (
        "assigned_to",
        "participants",
        "groups",
        "preceded_by",
        "creator",
        "latest_reviewer",
        "parent_occurrence",
    )

    inlines = [ActivityInline, ParticipantInline, CompanyInline]

    def reversion_register(self, model, **options):
        options = {
            "exclude": (
                "created",
                "creator",
                "edited",
            ),
        }
        super().reversion_register(model, **options)

    def get_queryset(self, request):
        return Activity.all_objects.all()


@admin.register(ActivityParticipant)
class ActivityParticipantAdmin(VersionAdmin):
    search_fields = ("activity", "participant")
    list_display = ("id", "activity", "participant", "participation_status")

    def reversion_register(self, model, **options):
        options = {
            "follow": (
                "activity",
                "participant",
                "participation_status",
            )
        }
        super().reversion_register(model, **options)
