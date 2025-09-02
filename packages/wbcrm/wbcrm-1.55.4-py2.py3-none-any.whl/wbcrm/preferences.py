from datetime import date, timedelta

from dynamic_preferences.registries import global_preferences_registry


def get_maximum_allowed_recurrent_date():
    global_preferences = global_preferences_registry.manager()
    return date.today() + timedelta(days=global_preferences["wbcrm__recurrence_maximum_allowed_days"])


def get_recurrence_maximum_count():
    global_preferences = global_preferences_registry.manager()
    return global_preferences["wbcrm__recurrence_maximum_count"]
