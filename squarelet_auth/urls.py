"""URL mappings for squarelet app"""

# Django
from django.urls import path

# SquareletAuth
from squarelet_auth import views

app_name = "squarelet_auth"
urlpatterns = [path("webhook/", views.webhook, name="webhook")]
