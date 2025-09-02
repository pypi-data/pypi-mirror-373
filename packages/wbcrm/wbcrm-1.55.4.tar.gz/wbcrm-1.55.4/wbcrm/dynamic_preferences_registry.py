from django.utils.translation import gettext as _
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import BooleanPreference, IntegerPreference

general = Section("wbcrm")


@global_preferences_registry.register
class CheckForMandatoryParticipants(BooleanPreference):
    section = general
    name = "mandatory_participants"
    default = True

    verbose_name = _("Check for mandatory participants")
    help_text = _(
        'Determines whether or not companies must be entered as participants in the "Companies" field for activities.'
    )


@global_preferences_registry.register
class RecurrenceActivityEndDate(IntegerPreference):
    section = general
    name = "recurrence_maximum_allowed_days"
    # this short default value, is just for the moment to test the process and until we know how to handle the recurring activities more efficient
    default = 10 * 365

    verbose_name = _("The default Maximum allowed days")


@global_preferences_registry.register
class RecurrenceActivityDateListLength(IntegerPreference):
    section = general
    name = "recurrence_maximum_count"
    # this short default value, is just for the moment to test the process and until we know how to handle the recurring activities more efficient
    default = 366

    # verbose_name = _("For each date in the date list we create a child activity.number at which the date list will be cut.")
