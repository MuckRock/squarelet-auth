"""Views for the squarelet auth app"""

# Django
from django.contrib import auth, messages
from django.http.response import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

# Standard Library
import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

# SquareletAuth
from squarelet_auth import settings
from squarelet_auth.tasks import pull_data

logger = logging.getLogger(__name__)


@csrf_exempt
def webhook(request):
    """Receive a cache invalidation webhook from squarelet"""

    type_ = request.POST.get("type", "")
    uuids = request.POST.getlist("uuids", "")
    timestamp = request.POST.get("timestamp", "")
    signature = request.POST.get("signature", "")

    # verify signature
    hmac_digest = hmac.new(
        key=settings.SOCIAL_AUTH_SQUARELET_SECRET.encode("utf8"),
        msg="{}{}{}".format(timestamp, type_, "".join(uuids)).encode("utf8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
    match = hmac.compare_digest(signature, hmac_digest)
    try:
        timestamp_current = int(timestamp) + 300 > time.time()
    except ValueError:
        return HttpResponseForbidden()
    if not match or not timestamp_current:
        return HttpResponseForbidden()

    # pull the new data asynchrnously
    for uuid in uuids:
        pull_data.delay(type_, uuid)
    return HttpResponse("OK")


def logout(request):
    url = settings.BASE_URL + "/"
    if "id_token" in request.session:
        params = {
            "id_token_hint": request.session["id_token"],
            "post_logout_redirect_uri": url,
        }
        redirect_url = "{}/openid/end-session?{}".format(
            settings.SQUARELET_URL, urlencode(params)
        )
    else:
        redirect_url = "index"
    auth.logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect(redirect_url)


def login(request):
    return redirect(reverse("social:begin", kwargs={"backend": "squarelet"}))


def signup(request):
    return redirect(f"{settings.SQUARELET_URL}/selectplan/?intent={settings.INTENT}")


def profile(request, username):
    return redirect(f"{settings.SQUARELET_URL}/users/{username}/")
