#!/usr/bin/env python

# Django
import django
from django.conf import settings
from django.core.management import call_command

settings.configure(
    DEBUG=True,
    INSTALLED_APPS=(
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "squarelet_auth.organizations.apps.OrganizationsConfig",
    ),
    SOCIAL_AUTH_SQUARELET_KEY="",
    SOCIAL_AUTH_SQUARELET_SECRET="",
    SQUARELET_ORGANIZATION_MODEL="squarelet_auth_organizations.Organization",
)

django.setup()
call_command("makemigrations", "squarelet_auth_organizations")
