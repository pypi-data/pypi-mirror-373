import os
from unittest.mock import sentinel

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def settings_or_environment(key, default=sentinel.NOTSET, raise_if_missing=True):
    """
    Checks django settings and then the environment for the specified key
    """
    try:
        return getattr(settings, key)
    except AttributeError:
        try:
            return os.environ[key]
        except KeyError:
            ...

    if raise_if_missing:
        raise ImproperlyConfigured(f"Could not find {key} in settings or environment")

    if default is not sentinel.NOTSET:
        return default

    return None
