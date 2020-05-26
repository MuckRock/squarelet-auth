# Django
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Standard Library
import logging
from uuid import uuid4

# SquareletAuth
from squarelet_auth import settings

logger = logging.getLogger(__name__)


class AbstractOrganization(models.Model):
    """An orginization users can belong to"""

    uuid = models.UUIDField(
        _("UUID"),
        unique=True,
        editable=False,
        default=uuid4,
        db_index=True,
        help_text=_("Unique ID to link organizations across MuckRock's sites"),
    )

    users = models.ManyToManyField(
        verbose_name=_("users"),
        to=settings.AUTH_USER_MODEL,
        through="squarelet_auth_organizations.Membership",
        related_name="organizations",
        help_text=_("The users who are members of this organization"),
    )

    name = models.CharField(
        _("name"), max_length=255, help_text=_("Name of the organization")
    )
    slug = models.SlugField(
        _("slug"),
        max_length=255,
        unique=True,
        help_text=_("Unique slug for the organization which may be used in a URL"),
    )
    private = models.BooleanField(
        _("private"),
        default=False,
        help_text=_(
            "Whether or not to keep this organization and its membership list private"
        ),
    )
    individual = models.BooleanField(
        _("individual"),
        default=True,
        help_text=_("Is this an organization for an individual user?"),
    )
    # XXX how to handle plans
    plan = models.ForeignKey(
        verbose_name=_("plan"),
        to="squarelet_auth_organizations.Plan",
        on_delete=models.PROTECT,
        null=True,
        help_text=_("The subscription type for this organization"),
    )
    card = models.CharField(
        _("card"),
        max_length=255,
        blank=True,
        help_text=_(
            "The brand and last 4 digits of the default credit card on file for this "
            "organization, for display purposes"
        ),
    )
    avatar_url = models.URLField(
        _("avatar url"),
        max_length=255,
        blank=True,
        help_text=_("A URL which points to an avatar for the organization"),
    )

    date_update = models.DateField(
        _("date update"),
        null=True,
        help_text=_(
            "The date when this organizations monthly resources will be refreshed"
        ),
    )

    payment_failed = models.BooleanField(
        _("payment failed"),
        default=False,
        help_text=_(
            "This organizations payment method has failed and should be updated"
        ),
    )
    verified_journalist = models.BooleanField(
        _("verified journalist"),
        default=False,
        help_text=_("This organization is a verified jorunalistic organization"),
    )

    class Meta:
        ordering = ("slug",)
        abstract = True

    def __str__(self):
        if self.individual:
            return f"{self.name} (Individual)"
        else:
            return self.name

    def get_absolute_url(self):
        return reverse(
            "squarelet_auth_organizations:profile", kwargs={"slug": self.slug}
        )

    @property
    def display_name(self):
        """Display 'Personal Account' for individual organizations"""
        if self.individual:
            return "Personal Account"
        else:
            return self.name

    def has_member(self, user):
        """Is the user a member of this organization?"""
        return self.users.filter(pk=user.pk).exists()

    def has_admin(self, user):
        """Is the user an admin of this organization?"""
        return self.users.filter(pk=user.pk, memberships__admin=True).exists()

    def update_data(self, data):
        """Set updated data from squarelet"""

        # plan should always be created on client sites before being used
        # get_or_create is used as a precauitionary measure
        self.plan, created = Plan.objects.get_or_create(
            slug=data["plan"], defaults={"name": data["plan"].replace("-", " ").title()}
        )
        if created:
            logger.warning("Unknown plan: %s", data["plan"])

        self._update_resources(data)

        # update the remaining fields
        fields = [
            "name",
            "slug",
            "individual",
            "private",
            "date_update",
            "card",
            "payment_failed",
            "avatar_url",
            "verified_journalist",
        ]
        for field in fields:
            if field in data:
                setattr(self, field, data[field])
        self.save()

    def _update_resources(self, data):
        """Allows subclasses to override to update their resources"""


class Organization(AbstractOrganization):
    class Meta:
        swappable = "SQUARELET_ORGANIZATION_MODEL"


class Membership(models.Model):
    """Through table for organization membership"""

    user = models.ForeignKey(
        verbose_name=_("user"),
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
        help_text=_("A user being linked to an organization"),
    )
    organization = models.ForeignKey(
        verbose_name=_("organization"),
        to=settings.ORGANIZATION_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
        help_text=_("An organization being linked to a user"),
    )
    active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_("The user is currently working on behalf of this organization"),
    )
    admin = models.BooleanField(
        _("admin"),
        default=False,
        help_text=_("The user is an administrator for this organization"),
    )

    class Meta:
        unique_together = ("user", "organization")

    def __str__(self):
        return f"{self.user} in {self.organization}"


class Plan(models.Model):
    """Plans that organizations can subscribe to"""

    name = models.CharField(_("name"), max_length=255, unique=True)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    resources = JSONField(default=dict)

    def __str__(self):
        return self.name
