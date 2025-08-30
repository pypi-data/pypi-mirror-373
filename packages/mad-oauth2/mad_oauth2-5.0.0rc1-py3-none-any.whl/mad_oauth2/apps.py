import contextlib

from django.apps import AppConfig


class Oauth2Config(AppConfig):
    name = "mad_oauth2"
    verbose_name = "Mad OAuth2"

    def ready(self):
        with contextlib.suppress(Exception):
            import mad_oauth2.signals  # noqa: F401, PLC0415
