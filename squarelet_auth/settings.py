# Django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SQUARELET_URL = getattr(settings, "SQUARELET_URL", "https://accounts.muckrock.com")

WHITELIST_VERIFIED_JOURNALISTS = getattr(
    settings, "SQUARELET_WHITELIST_VERIFIED_JOURNALISTS", False
)

DISABLE_CREATE = getattr(settings, "SQUARELET_DISABLE_CREATE", True)
DISABLE_CREATE_AGENCY = getattr(settings, "SQUARELET_DISABLE_CREATE_AGENCY", True)

BYPASS_RATE_LIMIT_SECRET = getattr(settings, "SQUARELET_BYPASS_RATE_LIMIT_SECRET", "")

INTENT = getattr(settings, "SQUARELET_INTENT", "")

RESOURCE_FIELDS = getattr(settings, "SQUARELET_RESOURCE_FIELDS", {})

required_settings = [
    "SOCIAL_AUTH_SQUARELET_KEY",
    "SOCIAL_AUTH_SQUARELET_SECRET",
    "SQUARELET_ORGANIZATION_MODEL",
    "BASE_URL",
]
for setting in required_settings:
    if not hasattr(settings, setting):
        raise ImproperlyConfigured(
            f"You must define {setting} in settings to use SquareletAuth"
        )

SOCIAL_AUTH_SQUARELET_KEY = settings.SOCIAL_AUTH_SQUARELET_KEY
SOCIAL_AUTH_SQUARELET_SECRET = settings.SOCIAL_AUTH_SQUARELET_SECRET
ORGANIZATION_MODEL = settings.SQUARELET_ORGANIZATION_MODEL
BASE_URL = getattr(settings, "BASE_URL")

AUTH_USER_MODEL = settings.AUTH_USER_MODEL
