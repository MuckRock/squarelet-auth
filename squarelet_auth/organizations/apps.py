# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrganizationsConfig(AppConfig):
    name = "squarelet_auth.organizations"
    label = "squarelet_auth_organizations"
    verbose_name = _("Organizations")
