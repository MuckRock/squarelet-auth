# Django
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import CICharField, CIEmailField
from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Standard Library
from uuid import uuid4

# SquareletAuth
from squarelet_auth.fields import AutoCreatedField, AutoLastModifiedField
from squarelet_auth.organizations import get_organization_model

Organization = get_organization_model()


class User(AbstractBaseUser, PermissionsMixin):

    uuid = models.UUIDField(
        _("UUID"),
        unique=True,
        editable=False,
        default=uuid4,
        db_index=True,
        help_text=_("Unique ID to link users across MuckRock's sites"),
    )
    name = models.CharField(
        _("full name"), max_length=255, help_text=_("The user's full name")
    )
    email = models.EmailField(
        _("email"),
        unique=True,
        null=True,
        help_text=_("The user's primary email address"),
        db_collation="case_insensitive",
    )
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_("A unique public identifier for the user"),
        db_collation="case_insensitive",
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
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
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

    created_at = AutoCreatedField(
        _("created at"), help_text=_("Timestamp of when the user was created")
    )
    updated_at = AutoLastModifiedField(
        _("updated at"), help_text=_("Timestamp of when the user was last updated")
    )

    # preferences
    use_autologin = models.BooleanField(
        _("use autologin"),
        default=True,
        help_text=(
            "Links you receive in emails from us will contain"
            " a token to automatically log you in"
        ),
    )

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        abstract = True
        ordering = ("username",)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("squarelet_auth:profile", kwargs={"username": self.username})

    @property
    def date_joined(self):
        """Alias date joined to create_at for third party apps"""
        return self.created_at

    def get_full_name(self):
        return self.name

    @property
    def organization(self):
        """Get the user's active organization"""
        # first check the prefetch cache, for performance reasons
        if hasattr(self, "active_memberships"):
            return self.active_memberships[0].organization

        return (
            self.memberships.select_related("organization")
            .get(active=True)
            .organization
        )

    @organization.setter
    def organization(self, organization):
        """Set the user's active organization"""
        if not organization.has_member(self):
            raise ValueError(
                "Cannot set a user's active organization to an organization "
                "they are not a member of"
            )
        with transaction.atomic():
            self.memberships.filter(active=True).update(active=False)
            self.memberships.filter(organization=organization).update(active=True)

    @property
    def individual_organization(self):
        """Get the user's individual organization
        There should always be exactly one individual organization,
        which has a matching UUID
        """
        return Organization.objects.get(uuid=self.uuid)

    @property
    def verified_journalist(self):
        """Is this user a member of a verified journalistic organization?"""
        return self.organizations.filter(verified_journalist=True).exists()
