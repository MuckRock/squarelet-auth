# Django
import django.dispatch
from django.contrib.auth import get_user_model
from django.db import transaction

# Standard Library
import logging

# SquareletAuth
from squarelet_auth import settings
from squarelet_auth.organizations import get_organization_model
from squarelet_auth.organizations.models import Membership
from squarelet_auth.organizations.utils import (
    squarelet_update_or_create as organization_update_or_create,
)

User = get_user_model()
Organization = get_organization_model()

logger = logging.getLogger(__name__)

user_update = django.dispatch.Signal()


@transaction.atomic
def squarelet_update_or_create(uuid, data):
    """Update or create users based on data from squarelet"""

    required_fields = {"preferred_username", "organizations"}
    missing = required_fields - (required_fields & set(data.keys()))
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    if data.get("is_agency") and settings.DISABLE_CREATE_AGENCY:
        # do not create agency users if they have been disabled
        return None, False

    user, created = _squarelet_update_or_create(uuid, data)

    _update_organizations(user, data)

    user_update.send(sender=User, user=user, data=data)

    return user, created


def _squarelet_update_or_create(uuid, data):
    """Format user data and update or create the user"""
    user_map = {
        "preferred_username": "username",
        "email": "email",
        "name": "name",
        "picture": "avatar_url",
        "email_failed": "email_failed",
        "email_verified": "email_verified",
        "use_autologin": "use_autologin",
        "bio": "bio",
    }
    user_defaults = {
        "preferred_username": "",
        "email": "",
        "name": "",
        "picture": "",
        "email_failed": False,
        "email_verified": False,
        "use_autologin": True,
        "bio": "",
    }
    user_data = {user_map[k]: data.get(k, user_defaults[k]) for k in user_map}
    return User.objects.update_or_create(uuid=uuid, defaults=user_data)


def _update_organizations(user, data):
    """Update the user's organizations"""
    logger.info("[SQ AUTH] Updating organizations for %s", user.username)
    current_organizations = set(user.organizations.all())
    new_memberships = []
    active = True

    # process each organization
    organizations = data.get("organizations", [])
    organizations.sort(key=lambda x: x["individual"])
    logger.info(
        "[SQ AUTH] Updating organizations for %s, organizations: %s",
        user.username,
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
            user.memberships.filter(organization=organization).update(
                admin=org_data["admin"]
            )
        else:
            # if not currently a member, create the new membership
            # automatically activate new organizations (only first one)
            new_memberships.append(
                Membership(
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
        user.memberships.filter(active=True).update(active=False)
        user.memberships.bulk_create(new_memberships)

    # user must have an active organization, if the current
    # active one is removed, we will activate the user's individual organization
    if user.organization in current_organizations:
        user.memberships.filter(organization__individual=True).update(active=True)

    # never remove the user's individual organization
    individual_organization = user.memberships.get(organization__individual=True)
    if individual_organization in current_organizations:
        logger.error("Trying to remove a user's individual organization: %s", user)
        current_organizations.remove(individual_organization)

    user.memberships.filter(organization__in=current_organizations).delete()
