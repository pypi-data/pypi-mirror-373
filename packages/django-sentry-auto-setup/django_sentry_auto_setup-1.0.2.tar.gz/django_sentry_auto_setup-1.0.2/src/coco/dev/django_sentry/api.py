import logging
import time

import httpx

from src.coco.dev.django_sentry.settings_helpers import settings_or_environment

log = logging.getLogger(__name__)


class SentryApiException(Exception):
    def __init__(self, message: str, *args, response, **kwargs):
        self.response = response
        super().__init__(message, *args, **kwargs)


def validate_settings():
    """
    Checks to make sure all the necessary settings are in place. The inner exception will
    :return:
    """
    log.info("Validating Sentry settings...")
    settings_or_environment('SENTRY_AUTH_TOKEN', raise_if_missing=True)
    settings_or_environment('SENTRY_HOST', raise_if_missing=True)
    settings_or_environment('SENTRY_ORGANIZATION_SLUG', raise_if_missing=True)
    settings_or_environment('SENTRY_TEAM_SLUG', raise_if_missing=True)
    settings_or_environment('SENTRY_PROJECT_NAME', raise_if_missing=True)
    settings_or_environment('SENTRY_PROJECT_SLUG', raise_if_missing=True)
    log.info("Sentry settings valid!")


def create_project():
    log.info("Ensuring project exists in Sentry...")
    sentry_host = settings_or_environment('SENTRY_HOST')
    organization_id_or_slug = settings_or_environment('SENTRY_ORGANIZATION_SLUG')
    team_id_or_slug = settings_or_environment('SENTRY_TEAM_SLUG')

    url = f"{sentry_host}api/0/teams/{organization_id_or_slug}/{team_id_or_slug}/projects/"
    response = httpx.post(
        url,
        json={
            "name": settings_or_environment('SENTRY_PROJECT_NAME'),
            "slug": settings_or_environment('SENTRY_PROJECT_SLUG'),
        },
        headers={
            "Authorization": f"Bearer {settings_or_environment('SENTRY_AUTH_TOKEN')}",
        }
    )

    match response.status_code:
        case 409:
            log.info("Project already exists in Sentry!")
        case 400:
            raise SentryApiException("Could not create project in Sentry!", response=response)
        case 403:
            raise SentryApiException(
                "Auth token for Sentry does not have the required scopes. "
                "See https://docs.sentry.io/api/projects/create-a-new-project/",
                response=response,
            )
        case 201:
            log.info("Project created in Sentry!")
        case _:
            log.debug("Unknown status code received from Sentry")

    return response


def get_project_dsn(project_id_or_slug):
    sentry_host = settings_or_environment('SENTRY_HOST')
    organization_id_or_slug = settings_or_environment('SENTRY_ORGANIZATION_SLUG')

    url = f"{sentry_host}api/0/teams/{organization_id_or_slug}/{project_id_or_slug}/keys/"
    response = httpx.get(
        url,
        params={
            'status': 'active',
        },
        headers={
            "Authorization": f"Bearer {settings_or_environment('SENTRY_AUTH_TOKEN')}",
        }
    )
    match response.status_code:
        case 403:
            raise SentryApiException(
                "Auth token for Sentry does not have the required scopes. "
                "See https://docs.sentry.io/api/projects/list-a-projects-client-keys/",
                response=response,
            )
        case 400:
            raise SentryApiException("Could not retrieve project DSN!", response=response)
        case 200:
            ...
        case _:
            log.debug("Unknown status code received from Sentry")

    as_json = response.json()
    if as_json:
        return as_json[0]['dsn']['public']
    else:
        return create_project_dsn(project_id_or_slug)


def create_project_dsn(project_id_or_slug):
    sentry_host = settings_or_environment('SENTRY_HOST')
    organization_id_or_slug = settings_or_environment('SENTRY_ORGANIZATION_SLUG')

    url = f"{sentry_host}api/0/teams/{organization_id_or_slug}/{project_id_or_slug}/keys/"
    response = httpx.post(
        url,
        headers={
            "Authorization": f"Bearer {settings_or_environment('SENTRY_AUTH_TOKEN')}",
        },
        json={
            'name': (
                f"{settings_or_environment('SENTRY_TEAM_SLUG')}-"
                f"{settings_or_environment('SENTRY_PROJECT_SLUG')}-"
                f"{time.ctime()}"
            ),
            'rateLimit': None,
            'useCase': 'user',
        }
    )
    match response.status_code:
        case 403:
            raise SentryApiException(
                "Auth token for Sentry does not have the required scopes. "
                "See https://docs.sentry.io/api/projects/create-a-new-client-key/",
                response=response,
            )
        case 400:
            raise SentryApiException("Could not create project key DSN!", response=response)
        case 201:
            log.info("Project key created in Sentry!")
        case _:
            log.debug("Unknown status code received from Sentry")

    return response.json()['dsn']['public']


def init_sdk(**sentry_kwargs):
    log.info("Initializing Sentry SDK for project...")
    import sentry_sdk

    sentry_kwargs.setdefault(
        'traces_sample_rate',
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        1.0,
    )

    sentry_sdk.init(
        dsn=get_project_dsn(settings_or_environment('SENTRY_PROJECT_SLUG')),
        **sentry_kwargs,
    )
    log.info("Sentry SDK for project initialized!")
