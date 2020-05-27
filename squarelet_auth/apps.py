# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SquareletAuthConfig(AppConfig):
    name = "squarelet_auth"
    verbose_name = _("Squarelet Auth")

    def ready(self):
        # require squarelet login for admin
        from django.contrib.auth.decorators import login_required
        from django.contrib import admin

        admin.site.login = login_required(admin.site.login)
