"""
Backend to support OIDC login through Squarelet
"""

# Third Party
from social_core.backends.open_id_connect import OpenIdConnectAuth

# SquareletAuth
from squarelet_auth import settings


class SquareletBackend(OpenIdConnectAuth):
    """Authentication Backend for Squarelet OpenId"""

    # pylint: disable=abstract-method
    name = "squarelet"
    OIDC_ENDPOINT = settings.SQUARELET_URL + "/openid"

    def auth_allowed(self, response, details):
        if settings.WHITELIST_VERIFIED_JOURNALISTS:
            return any(o["verified_journalist"] for o in response["organizations"])
        else:
            return True
