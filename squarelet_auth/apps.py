# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SquareletAuthConfig(AppConfig):
    name = "squarelet_auth"
    verbose_name = _("Squarelet Auth")
