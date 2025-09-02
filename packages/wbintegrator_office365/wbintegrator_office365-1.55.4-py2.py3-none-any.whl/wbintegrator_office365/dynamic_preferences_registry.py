from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import StringPreference

general = Section("wbintegrator_office365")


@global_preferences_registry.register
class AccesTokenPreference(StringPreference):
    section = general
    name = "access_token"
    default = "0"

    verbose_name = "Access Token"
    help_text = "The access token obtained from subscriptions Microsoft for authentication"
