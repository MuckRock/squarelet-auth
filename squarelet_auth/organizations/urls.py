# Django
from django.urls import path

# SquareletAuth
from squarelet_auth.organizations import views

app_name = "squarelet_auth_organizations"
urlpatterns = [
    path("profile/<slug:slug>/", views.profile, name="profile"),
]
