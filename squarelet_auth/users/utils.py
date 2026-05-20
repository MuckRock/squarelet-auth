# Django
import django.dispatch
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.module_loading import import_string

# Standard Library
import logging

# SquareletAuth
from squarelet_auth import settings
from squarelet_auth.organizations.models import SquareletMembership
from squarelet_auth.organizations.utils import (
    squarelet_update_or_create as organization_update_or_create,
)

logger = logging.getLogger(__name__)

user_update = django.dispatch.Signal()


@transaction.atomic
def squarelet_update_or_create(uuid, data, user=None):
    """Update or create users based on data from squarelet"""

    required_fields = {"preferred_username", "organizations"}
    missing = required_fields - (required_fields & set(data.keys()))
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    if data.get("is_agency") and settings.DISABLE_CREATE_AGENCY:
        # do not create agency users if they have been disabled
        return None, False

    user, created = _squarelet_update_or_create(uuid, data, user=user)

    _update_organizations(user, data)

    User = get_user_model()
    user_update.send(sender=User, user=user, data=data)

    return user, created


def _squarelet_update_or_create(uuid, data, user=None):
    """Format profile data and update or create the SquareletProfile"""
    from squarelet_auth.users.models import SquareletProfile

    profile_map = {
        "preferred_username": "username",
        "email": "email",
        "name": "name",
        "picture": "avatar_url",
        "email_failed": "email_failed",
        "email_verified": "email_verified",
        "use_autologin": "use_autologin",
        "bio": "bio",
    }
    profile_defaults = {
        "preferred_username": "",
        "email": "",
        "name": "",
        "picture": "",
        "email_failed": False,
        "email_verified": False,
        "use_autologin": True,
        "bio": "",
    }
    profile_data = {
        profile_map[k]: data.get(k, profile_defaults[k]) for k in profile_map
    }

    try:
        profile = SquareletProfile.objects.get(uuid=uuid)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        return profile.user, False
    except SquareletProfile.DoesNotExist:
        if user is None:
            user = _create_user(uuid, data)
        profile = SquareletProfile.objects.create(uuid=uuid, user=user, **profile_data)
        return user, True


def _create_user(uuid, data):
    """Create a new host-app User for the given Squarelet data.

    If SQUARELET_CREATE_USER is set, calls that callable (dotted path).
    Otherwise creates a user with username and email from Squarelet data.
    """
    User = get_user_model()
    if settings.CREATE_USER:
        factory = import_string(settings.CREATE_USER)
        return factory(uuid, data)

    username = data.get("preferred_username", "")
    email = data.get("email") or None
    return User.objects.create_user(username=username, email=email)


def _update_organizations(user, data):
    """Update the user's organizations"""
    logger.info("[SQ AUTH] Updating organizations for %s", user)
    current_organizations = set(user.squarelet_organizations.all())
    new_memberships = []
    active = True

    # process each organization
    organizations = data.get("organizations", [])
    organizations.sort(key=lambda x: x["individual"])
    logger.info(
        "[SQ AUTH] Updating organizations for %s, organizations: %s",
        user,
        ", ".join(o["name"] for o in organizations),
    )
    for org_data in organizations:
        logger.info("[SQ AUTH] Org data: %s", org_data)
        organization, _ = organization_update_or_create(
            uuid=org_data["uuid"], data=org_data
        )
        if organization in current_organizations:
            # remove organizations from our set as we see them
            # any that are left will need to be removed
            current_organizations.remove(organization)
            user.squarelet_memberships.filter(organization=organization).update(
                admin=org_data["admin"]
            )
        else:
            # if not currently a member, create the new membership
            # automatically activate new organizations (only first one)
            new_memberships.append(
                SquareletMembership(
                    user=user,
                    organization=organization,
                    active=active,
                    admin=org_data["admin"],
                )
            )
            active = False

    if new_memberships:
        # first new membership will be made active, de-activate current
        # active org first
        user.squarelet_memberships.filter(active=True).update(active=False)
        user.squarelet_memberships.bulk_create(new_memberships)

    # user must have an active organization, if the current
    # active one is removed, we will activate the user's individual organization
    if user.squarelet_profile.organization in current_organizations:
        user.squarelet_memberships.filter(organization__individual=True).update(
            active=True
        )

    # never remove the user's individual organization
    individual_organization = user.squarelet_memberships.get(
        organization__individual=True
    )
    if individual_organization in current_organizations:
        logger.error("Trying to remove a user's individual organization: %s", user)
        current_organizations.remove(individual_organization)

    user.squarelet_memberships.filter(organization__in=current_organizations).delete()
