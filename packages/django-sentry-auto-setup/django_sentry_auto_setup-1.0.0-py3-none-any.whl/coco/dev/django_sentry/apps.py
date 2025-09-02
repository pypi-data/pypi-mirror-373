from django.apps import AppConfig

from src.coco.dev.django_sentry.signals import on_ready


class AutomaticSentryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mrsage.discrete.automatic_sentry_setup'

    def ready(self):
        on_ready()
