# Django
from django.conf import settings
from django.shortcuts import redirect


def profile(request, slug):
    return redirect(f"{settings.SQUARELET_URL}/organizations/{slug}/")
