# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.http import is_safe_url

# SquareletAuth
from squarelet_auth.organizations.models import SquareletOrganization


@login_required
def activate(request):
    """Activate one of your organizations"""
    redirect_url = request.POST.get("next", "/")
    redirect_url = redirect_url if is_safe_url(redirect_url, allowed_hosts=[]) else "/"

    try:
        organization = request.user.squarelet_organizations.get(
            pk=request.POST.get("organization")
        )
        request.user.squarelet_profile.organization = organization
        messages.success(
            request,
            "You have switched your active organization to {}".format(
                organization.display_name
            ),
        )
    except SquareletOrganization.DoesNotExist:
        messages.error(request, "Organization does not exist")
    except ValueError:
        messages.error(request, "You are not a member of that organization")

    return redirect(redirect_url)


def profile(request, slug):
    return redirect(f"{settings.SQUARELET_URL}/organizations/{slug}/")
