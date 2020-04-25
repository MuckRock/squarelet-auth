"""
Custom pipeline steps for oAuth authentication
"""
# Django
from django.contrib.auth import get_user_model

# Standard Library
import logging

# SquareletAuth
from squarelet_auth.users.utils import squarelet_update_or_create

User = get_user_model()

logger = logging.getLogger(__name__)

# pylint: disable=inconsistent-return-statements


def associate_by_uuid(response, user=None, *args, **kwargs):
    """Associate current auth with a user with the same uuid in the DB."""
    # pylint: disable=unused-argument,keyword-arg-before-vararg

    uuid = response.get("uuid")
    if uuid:
        try:
            user = User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            return None
        else:
            return {"user": user, "is_new": False}


def save_info(response, *args, **kwargs):
    """Update the user's info based on information from squarelet"""
    # pylint: disable=unused-argument
    user, created = squarelet_update_or_create(response["uuid"], response)
    return {"user": user, "is_new": created}


def save_session_data(strategy, request, response, *args, **kwargs):
    """Save some data in the session"""
    # pylint: disable=unused-argument
    # session_state and id_token are used for universal logout functionality
    session_state = strategy.request_data().get("session_state")
    if session_state:
        request.session["session_state"] = session_state

    id_token = response.get("id_token")
    if id_token:
        request.session["id_token"] = id_token
