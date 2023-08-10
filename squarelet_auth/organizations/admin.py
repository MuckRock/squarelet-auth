# Django
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.safestring import mark_safe

# SquareletAuth
from squarelet_auth import settings
from squarelet_auth.organizations.models import Entitlement, Organization

User = get_user_model()


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Organization Admin"""

    list_display = (
        "name",
        "entitlement",
        "private",
        "individual",
        "verified_journalist",
    )
    list_filter = ("entitlement", "private", "individual", "verified_journalist")
    search_fields = ("name",)
    fields = (
        "uuid",
        "name",
        "slug",
        "private",
        "individual",
        "verified_journalist",
        "entitlement",
        "card",
        "date_update",
    )
    readonly_fields = (
        "uuid",
        "name",
        "slug",
        "private",
        "individual",
        "verified_journalist",
        "entitlement",
        "card",
        "date_update",
    )
    list_select_related = ("entitlement",)
    save_on_top = True

    def get_fields(self, request, obj=None):
        """Only add user link for individual organizations"""
        if obj and obj.individual:
            return ("user_link",) + self.fields
        else:
            return self.fields

    def get_readonly_fields(self, request, obj=None):
        """Only add user link for individual organizations"""
        if obj and obj.individual:
            return ("user_link",) + self.readonly_fields
        else:
            return self.readonly_fields

    @mark_safe
    def user_link(self, obj):
        """Link to the individual org's user"""
        user = User.objects.get(uuid=obj.uuid)
        link = reverse(
            "admin:{}_change".format(
                settings.AUTH_USER_MODEL.lower().replace(".", "_")
            ),
            args=(user.pk,),
        )
        return '<a href="%s">%s</a>' % (link, user.username)

    user_link.short_description = "User"


@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin):
    """Entitlement Admin"""

    list_display = ("name",) + tuple(settings.RESOURCE_FIELDS.keys())
    readonly_fields = ("name", "slug", "description", "resources")
