.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/django-sentry-auto-setup.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/django-sentry-auto-setup
    .. image:: https://readthedocs.org/projects/django-sentry-auto-setup/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://django-sentry-auto-setup.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/django-sentry-auto-setup/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/django-sentry-auto-setup
    .. image:: https://img.shields.io/pypi/v/django-sentry-auto-setup.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/django-sentry-auto-setup/
    .. image:: https://img.shields.io/conda/vn/conda-forge/django-sentry-auto-setup.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/django-sentry-auto-setup
    .. image:: https://pepy.tech/badge/django-sentry-auto-setup/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/django-sentry-auto-setup
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/django-sentry-auto-setup

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

========================
django-sentry-auto-setup
========================


    Handsfree setup of your Django project inside of Sentry!


Tired of setting up Sentry by hand? Me too! So here is a little package that
quickly sets up a Django project automatically.

Install
=======

::

    pip install django-sentry-auto-setup


Configure
=========

Set these values in your environment or your Django settings file:

::

    SENTRY_AUTH_TOKEN
    SENTRY_ENABLE_AUTO_SETUP
    SENTRY_HOST
    SENTRY_ORGANIZATION_SLUG
    SENTRY_PROJECT_NAME
    SENTRY_PROJECT_SLUG
    SENTRY_TEAM_SLUG

If you need to further configure the Sentry SDK also set this in Django settings:

::

    SENTRY_SDK_KWARGS

.. _pyscaffold-notes:

Making Changes & Contributing
=============================

This project uses `pre-commit`_, please make sure to install it before making any
changes::

    pip install pre-commit
    cd django-sentry-auto-setup
    pre-commit install

It is a good idea to update the hooks to the latest version::

    pre-commit autoupdate

Don't forget to tell your contributors to also install and use pre-commit.

.. _pre-commit: https://pre-commit.com/

Note
====

This project has been set up using PyScaffold 4.6. For details and usage
information on PyScaffold see https://pyscaffold.org/.
