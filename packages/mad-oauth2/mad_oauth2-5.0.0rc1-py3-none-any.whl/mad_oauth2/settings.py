from django.conf import settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string

USER_SETTINGS = getattr(settings, "MAD_OAUTH2", None)

DEFAULTS = {
    "THROTTLE_CLASS": "mad_oauth2.throttling.ThrottleClass",
    "OAUTH2_PROVIDER": {
        "SCOPES_BACKEND_CLASS": "mad_oauth2.oauth2.ApplicationScopes",
        "APPLICATION_ADMIN_CLASS": "mad_oauth2.admin.ApplicationAdminClass",
    },
}

IMPORT_STRINGS = ("THROTTLE_CLASS",)
MANDATORY = IMPORT_STRINGS


def perform_import(val, setting_name):
    if val is None:
        return None
    if isinstance(val, str):
        return import_from_string(val, setting_name)
    if isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    try:
        return import_string(val)
    except ImportError as e:
        msg = f"Could not import {val!r} for setting {setting_name!r}. {e.__class__.__name__}: {e}."  # noqa: E501
        raise ImportError(msg)  # noqa: B904


class MadOauth2Settings:
    def __init__(
        self, user_settings=None, defaults=None, import_strings=None, mandatory=None
    ):
        self._user_settings = user_settings or {}
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self.mandatory = mandatory or ()
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "MAD_OAUTH2", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            msg = f"Invalid MAD_OAUTH2 setting: {attr}"
            raise AttributeError(msg)

        try:
            val = self.user_settings[attr]
        except KeyError:
            val = self.defaults[attr]

        # Special merge for OAUTH2_PROVIDER dict
        if attr == "OAUTH2_PROVIDER":
            user_provider_settings = getattr(settings, "OAUTH2_PROVIDER", {})
            val = {**val, **user_provider_settings}

        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        self.validate_setting(attr, val)
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def validate_setting(self, attr, val):
        if not val and attr in self.mandatory:
            msg = f"mad_oauth2 setting: {attr} is mandatory"
            raise AttributeError(msg)

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


oauth2_settings = MadOauth2Settings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS, MANDATORY)


def reload_mad_oauth2_settings(*args, **kwargs):
    if kwargs["setting"] == "MAD_OAUTH2":
        oauth2_settings.reload()


setting_changed.connect(reload_mad_oauth2_settings)
