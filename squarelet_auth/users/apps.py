# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "squarelet_auth.users"
    label = "squarelet_auth_users"
    verbose_name = _("Squarelet Users")
