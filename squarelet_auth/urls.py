"""URL mappings for squarelet app"""

# Django
from django.urls import path

# SquareletAuth
from squarelet_auth import views

app_name = "squarelet_auth"
urlpatterns = [
    path("webhook/", views.webhook, name="webhook"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("profile/<str:username>/", views.profile, name="profile"),
]
