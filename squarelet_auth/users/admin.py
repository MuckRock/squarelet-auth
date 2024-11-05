# Django
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.db.models.functions.comparison import Collate
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# SquareletAuth
from squarelet_auth import settings


class UserAdmin(AuthUserAdmin):
    fieldsets = (
        (None, {"fields": ("uuid", "username", "org_link", "all_org_links")}),
        (_("Personal info"), {"fields": ("name", "email", "email_failed")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "created_at", "updated_at")}),
    )
    readonly_fields = (
        "uuid",
        "username",
        "org_link",
        "all_org_links",
        "name",
        "email",
        "last_login",
        "created_at",
        "updated_at",
    )
    list_display = (
        "username",
        "name",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    search_fields = ("username_deterministic", "name", "email_deterministic")

    def get_queryset(self, request):
        """Add deterministic fields for username and email so they
        can be searched"""
        return (
            super()
            .get_queryset(request)
            .annotate(
                email_deterministic=Collate("email", "und-x-icu"),
                username_deterministic=Collate("username", "und-x-icu"),
            )
        )

    @mark_safe
    def org_link(self, obj):
        """Link to the individual org"""
        link = reverse(
            "admin:{}_change".format(
                settings.ORGANIZATION_MODEL.lower().replace(".", "_")
            ),
            args=(obj.individual_organization.pk,),
        )
        return f'<a href="{link}">{obj.individual_organization.name}</a>'

    org_link.short_description = "Individual Organization"

    @mark_safe
    def all_org_links(self, obj):
        """Link to the user's other orgs"""
        orgs = obj.organizations.filter(individual=False)
        links = []
        for org in orgs:
            links.append(
                (
                    reverse(
                        "admin:{}_change".format(
                            settings.ORGANIZATION_MODEL.lower().replace(".", "_")
                        ),
                        args=(org.pk,),
                    ),
                    org.name,
                )
            )
        return ", ".join(f'<a href="{link}">{name}</a>' for link, name in links)

    all_org_links.short_description = "All Organizations"
