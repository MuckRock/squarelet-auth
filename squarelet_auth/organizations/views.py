# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.http import is_safe_url

# SquareletAuth
from squarelet_auth.organizations import get_organization_model

Organization = get_organization_model()


@login_required
def activate(request):
    """Activate one of your organizations"""
    redirect_url = request.POST.get("next", "/")
    redirect_url = redirect_url if is_safe_url(redirect_url, allowed_hosts=[]) else "/"

    try:
        organization = request.user.organizations.get(
            pk=request.POST.get("organization")
        )
        request.user.organization = organization
        messages.success(
            request,
            "You have switched your active organization to {}".format(
                organization.display_name
            ),
        )
    except Organization.DoesNotExist:
        messages.error(request, "Organization does not exist")
    except ValueError:
        messages.error(request, "You are not a member of that organization")

    return redirect(redirect_url)


def profile(request, slug):
    return redirect(f"{settings.SQUARELET_URL}/organizations/{slug}/")
