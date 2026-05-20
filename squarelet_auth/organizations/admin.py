# Django
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.safestring import mark_safe

# SquareletAuth
from squarelet_auth import settings
from squarelet_auth.organizations.models import Entitlement, SquareletOrganization


@admin.register(SquareletOrganization)
class SquareletOrganizationAdmin(admin.ModelAdmin):
    """SquareletOrganization Admin"""

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
        User = get_user_model()
        user = User.objects.get(squarelet_profile__uuid=obj.uuid)
        link = reverse(
            f"admin:{user._meta.app_label}_{user._meta.model_name}_change",
            args=(user.pk,),
        )
        return '<a href="%s">%s</a>' % (link, user)

    user_link.short_description = "User"


@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin):
    """Entitlement Admin"""

    list_display = ("name",) + tuple(settings.RESOURCE_FIELDS.keys())
    readonly_fields = ("name", "slug", "description", "resources")
