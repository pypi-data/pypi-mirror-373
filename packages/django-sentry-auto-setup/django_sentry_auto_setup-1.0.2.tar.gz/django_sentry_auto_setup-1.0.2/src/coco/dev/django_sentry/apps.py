from django.apps import AppConfig

from src.coco.dev.django_sentry.signals import on_ready


class AutomaticSentryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coco.dev.django_sentry'

    def ready(self):
        on_ready()
