"""Celery tasks for squarelet auth app"""

# Django
from celery import shared_task

# Standard Library
import logging

# Third Party
import requests

# SquareletAuth
from squarelet_auth.organizations.models import SquareletOrganization
from squarelet_auth.organizations.utils import (
    squarelet_update_or_create as org_update_or_create,
)
from squarelet_auth.users.utils import (
    squarelet_update_or_create as user_update_or_create,
)
from squarelet_auth.utils import squarelet_get

logger = logging.getLogger(__name__)


@shared_task(autoretry_for=(requests.exceptions.RequestException,), retry_backoff=1)
def pull_data(type_, uuid, **kwargs):
    """Task to pull data from squarelet"""
    # pylint: disable=unused-argument
    from squarelet_auth.users.models import SquareletProfile

    types_url = {"user": "users", "organization": "organizations"}
    types_update = {"user": user_update_or_create, "organization": org_update_or_create}
    if type_ not in types_url:
        logger.warning("Pull data received invalid type: %s", type_)
        return

    if type_ == "user":
        if not SquareletProfile.objects.filter(uuid=uuid).exists():
            # never create users from webhooks — users must log in via OAuth first
            return
    else:
        if not SquareletOrganization.objects.filter(uuid=uuid).exists():
            # never create organizations from webhooks if they have no local presence
            return

    resp = squarelet_get("/api/{}/{}/".format(types_url[type_], uuid))
    resp.raise_for_status()
    data = resp.json()
    logger.info("Pull data for: %s %s %s", type_, uuid, data)

    update_or_create = types_update[type_]
    update_or_create(uuid, data)
