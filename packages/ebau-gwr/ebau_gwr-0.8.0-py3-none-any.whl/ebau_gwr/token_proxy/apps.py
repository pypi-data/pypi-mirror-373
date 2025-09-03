from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured


class TokenProxyConfig(AppConfig):
    name = "ebau_gwr.token_proxy"

    def ready(self):
        from django.conf import settings

        from .app_settings import DEFAULTS, REQUIRED_SETTINGS

        for setting_key, setting_value in DEFAULTS.items():
            setattr(
                settings, setting_key, getattr(settings, setting_key, setting_value)
            )

        missing_settings = ", ".join(
            [setting for setting in REQUIRED_SETTINGS if not hasattr(settings, setting)]
        )
        if missing_settings:
            raise ImproperlyConfigured(
                f"Following settings are missing in your settings module: {missing_settings}."
            )
