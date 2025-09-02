from dynamic_preferences.registries import global_preferences_registry


def can_sync_past_activity() -> bool:
    return global_preferences_registry.manager()["wbactivity_sync__sync_past_activity"]


def can_sync_cancelled_activity() -> bool:
    return global_preferences_registry.manager()["wbactivity_sync__sync_cancelled_activity"]


def can_sync_cancelled_external_activity() -> bool:
    return global_preferences_registry.manager()["wbactivity_sync__sync_cancelled_external_activity"]


def can_sync_create_new_activity_on_replanned_reviewed_activity() -> bool:
    return global_preferences_registry.manager()[
        "wbactivity_sync__sync_create_new_activity_on_replanned_reviewed_activity"
    ]


def can_synchronize_activity_description() -> bool:
    return global_preferences_registry.manager()["wbactivity_sync__sync_activity_description"]


def can_synchronize_external_participants() -> bool:
    return global_preferences_registry.manager()["wbactivity_sync__sync_external_participants"]
