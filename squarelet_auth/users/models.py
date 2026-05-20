# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# Standard Library
from uuid import uuid4

# SquareletAuth
from squarelet_auth import settings
from squarelet_auth.fields import AutoCreatedField, AutoLastModifiedField


class SquareletProfile(models.Model):
    """Squarelet profile data linked to a host app's User model"""

    user = models.OneToOneField(
        verbose_name=_("user"),
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="squarelet_profile",
        help_text=_("The user this profile belongs to"),
    )
    uuid = models.UUIDField(
        _("UUID"),
        unique=True,
        db_index=True,
        default=uuid4,
        help_text=_("Unique ID to link users across MuckRock's sites"),
    )
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_("A unique public identifier for the user"),
    )
    email = models.EmailField(
        _("email"),
        unique=True,
        null=True,
        blank=True,
        help_text=_("The user's primary email address"),
    )
    name = models.CharField(
        _("full name"), max_length=255, blank=True, help_text=_("The user's full name")
    )
    avatar_url = models.URLField(
        _("avatar url"),
        blank=True,
        max_length=255,
        help_text=_("A URL which points to an avatar for the user"),
    )
    bio = models.TextField(
        _("bio"), blank=True, help_text=_("Public bio for the user, in Markdown")
    )
    email_failed = models.BooleanField(
        _("email failed"),
        default=False,
        help_text=_("Has an email we sent to this user's email address failed?"),
    )
    email_verified = models.BooleanField(
        _("email verified"),
        default=False,
        help_text=_("Has this user's email address been verified?"),
    )
    use_autologin = models.BooleanField(
        _("use autologin"),
        default=True,
        help_text=(
            "Links you receive in emails from us will contain"
            " a token to automatically log you in"
        ),
    )
    created_at = AutoCreatedField(
        _("created at"), help_text=_("Timestamp of when the profile was created")
    )
    updated_at = AutoLastModifiedField(
        _("updated at"),
        help_text=_("Timestamp of when the profile was last updated"),
    )

    class Meta:
        ordering = ("username",)

    def __str__(self):
        return self.username

    @property
    def individual_organization(self):
        """Get the user's individual organization
        There should always be exactly one individual organization,
        which has a matching UUID
        """
        from squarelet_auth.organizations.models import SquareletOrganization

        return SquareletOrganization.objects.get(uuid=self.uuid)

    @property
    def verified_journalist(self):
        """Is this user a member of a verified journalistic organization?"""
        return self.user.squarelet_memberships.filter(
            organization__verified_journalist=True
        ).exists()
