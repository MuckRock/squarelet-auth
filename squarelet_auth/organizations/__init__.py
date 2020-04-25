# Django
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

# SquareletAuth
from squarelet_auth import settings


def get_organization_model():
    """
    Return the Organization model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.ORGANIZATION_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "SQUARELET_ORGANIZATION_MODEL must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            f"SQUARELET_ORGANIZATION_MODEL refers to model "
            f"'{settings.ORGANIZATION_MODEL}' that has not been installed"
        )
