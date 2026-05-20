# Django
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# SquareletAuth
from squarelet_auth.users.models import SquareletProfile


@admin.register(SquareletProfile)
class SquareletProfileAdmin(admin.ModelAdmin):
    """Admin for SquareletProfile — Squarelet-synced data for each user"""

    list_display = ("username", "name", "email", "email_verified", "use_autologin")
    list_filter = ("email_verified", "email_failed", "use_autologin")
    search_fields = ("username", "name", "email")
    readonly_fields = (
        "user",
        "uuid",
        "username",
        "name",
        "email",
        "avatar_url",
        "bio",
        "email_failed",
        "email_verified",
        "use_autologin",
        "created_at",
        "updated_at",
    )
    fields = readonly_fields


class SquareletProfileInline(admin.StackedInline):
    """Inline for third-party apps to include in their UserAdmin"""

    model = SquareletProfile
    extra = 0
    readonly_fields = (
        "uuid",
        "username",
        "name",
        "email",
        "avatar_url",
        "bio",
        "email_failed",
        "email_verified",
        "use_autologin",
        "created_at",
        "updated_at",
    )
    fields = readonly_fields
    can_delete = False
    verbose_name_plural = _("Squarelet Profile")
