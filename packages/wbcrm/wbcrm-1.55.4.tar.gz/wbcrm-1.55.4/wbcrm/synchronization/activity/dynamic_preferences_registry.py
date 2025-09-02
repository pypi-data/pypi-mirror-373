from django.utils.translation import gettext as _
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import BooleanPreference, StringPreference

general = Section("wbactivity_sync")


@global_preferences_registry.register
class BackendCalendarPreference(StringPreference):
    section = general
    name = "sync_backend_calendar"
    default = ""

    verbose_name = _("Synchronization Backend Calendar")
    help_text = _("The Backend Calendar to synchronize activities with an external calendar.")


@global_preferences_registry.register
class SyncPastActivity(BooleanPreference):
    section = general
    name = "sync_past_activity"
    default = False

    verbose_name = _("Synchronization Past Activity")


@global_preferences_registry.register
class SyncCancelledActivity(BooleanPreference):
    section = general
    name = "sync_cancelled_activity"
    default = True

    verbose_name = _("Cancel Internal Activity Instead Of Deleting")
    help_text = _(
        "When an activity is deleted in an external calendar the corresponding workbench activity can be cancelled (default) or also deleted."
    )


@global_preferences_registry.register
class SyncCancelledExternalActivity(BooleanPreference):
    section = general
    name = "sync_cancelled_external_activity"
    default = False

    verbose_name = _("Cancel External Activity With One Non-Attending Internal Participant")
    help_text = _(
        "When an activity was created by an external person and has only one internal participant the activity in the workbench can be canceled if this participant doesn't choose to attend."
    )


@global_preferences_registry.register
class SyncActivityDescription(BooleanPreference):
    section = general
    name = "sync_activity_description"
    default = True

    verbose_name = _("Synchronize Activity Description")


@global_preferences_registry.register
class SyncExternalParticipants(BooleanPreference):
    section = general
    name = "sync_external_participants"
    default = False

    verbose_name = _("Synchronize External Participants From Internal Calendar To External Calendar")


@global_preferences_registry.register
class SyncReplannedReviewedActivityCreatesNewActivity(BooleanPreference):
    section = general
    name = "sync_create_new_activity_on_replanned_reviewed_activity"
    default = False

    verbose_name = _("Create New Activity When Replanning Passed Reviewed Activities")
    help_text = _(
        "If an activity with a past end date (already passed and reviewed) is moved to a future date, a new activity will automatically be created for the updated schedule."
    )


@global_preferences_registry.register
class GoogleSyncCredentials(StringPreference):
    section = general
    name = "google_sync_credentials"
    default = ""
    verbose_name = _("Google Synchronization Credentials")
    help_text = "Dict. Keys: 'url', 'type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 'client_x509_cert_url'"


@global_preferences_registry.register
class OutlookSyncCredentials(StringPreference):
    section = general
    name = "outlook_sync_credentials"
    default = ""
    verbose_name = _("Outlook Synchronization Credentials")
    help_text = '{"notification_url": "", "authority": "", "client_id": "", "client_secret": "", "token_endpoint": "", "graph_url": ""}'


@global_preferences_registry.register
class OutlookSyncAccesToken(StringPreference):
    section = general
    name = "outlook_sync_access_token"
    default = ""

    verbose_name = _("Microsoft Graph Access Token")
    help_text = _("The access token obtained from subscriptions to Microsoft used for authentication pruposes")


@global_preferences_registry.register
class OutlookSyncClientState(StringPreference):
    section = general
    name = "outlook_sync_client_state"
    default = "secretClientValue"

    verbose_name = _("Microsoft Graph Webhook Secret Client State")
    help_text = _(
        "Secret Client Value defined during subscription, it will be injected into the webhook notification against spoofing"
    )
