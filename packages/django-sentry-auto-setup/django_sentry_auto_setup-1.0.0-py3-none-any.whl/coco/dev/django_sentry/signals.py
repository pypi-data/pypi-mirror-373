from django.conf import settings

from src.coco.dev.django_sentry.api import create_project, init_sdk, validate_settings
from src.coco.dev.django_sentry.settings_helpers import settings_or_environment


def on_ready():
    if settings_or_environment('SENTRY_ENABLE_AUTO_SETUP', default=False, raise_if_missing=False) == "true":
        validate_settings()
        create_project()
        init_sdk(
            **getattr(settings, 'SENTRY_SDK_KWARGS', {})
        )
