"""Celery tasks for squarelet auth app"""

# Django
from celery import shared_task
from django.contrib.auth import get_user_model

# Standard Library
import logging

# Third Party
import requests

# SquareletAuth
from squarelet_auth import settings
from squarelet_auth.organizations import get_organization_model
from squarelet_auth.organizations.utils import (
    squarelet_update_or_create as org_update_or_create,
)
from squarelet_auth.users.utils import (
    squarelet_update_or_create as user_update_or_create,
)
from squarelet_auth.utils import squarelet_get

logger = logging.getLogger(__name__)


Organization = get_organization_model()


User = get_user_model()


@shared_task(autoretry_for=(requests.exceptions.RequestException,), retry_backoff=1)
def pull_data(type_, uuid, **kwargs):
    """Task to pull data from squarelet"""
    # pylint: disable=unused-argument
    types_url = {"user": "users", "organization": "organizations"}
    types_model = {"user": User, "organization": Organization}
    types_update = {"user": user_update_or_create, "organization": org_update_or_create}
    if type_ not in types_url:
        logger.warning("Pull data received invalid type: %s", type_)
        return

    model = types_model[type_]
    if settings.DISABLE_CREATE and not model.objects.filter(uuid=uuid).exists():
        # if we have disabled creating new instances from squarelet
        # do not try to pull the data unless the instance already exists locally
        return

    resp = squarelet_get("/api/{}/{}/".format(types_url[type_], uuid))
    resp.raise_for_status()
    data = resp.json()
    logger.info("Pull data for: %s %s %s", type_, uuid, data)

    update_or_create = types_update[type_]
    update_or_create(uuid, data)
