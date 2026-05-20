# SquareletAuth

A Django package for authenticating against the [MuckRock Squarelet](https://accounts.muckrock.com) user service. Designed for **third-party apps** that have their own `User` model — Squarelet data is stored in separate linked models (`SquareletProfile`, `SquareletOrganization`) rather than requiring your app to inherit from abstract base classes.

---

## How It Works

When a user logs in via Squarelet OAuth, the pipeline:

1. Looks up an existing `SquareletProfile` by UUID (the `associate_by_uuid` step)
2. If not found, lets `social_core` create or find the host app's `User` object
3. Creates/updates a `SquareletProfile` linked to that `User`
4. Syncs the user's organizations and memberships into `SquareletOrganization` / `SquareletMembership`

Squarelet data is also kept in sync via **webhooks** — Squarelet POSTs to your app when user or organization data changes, triggering a Celery task to pull fresh data.

---

## Requirements

- Python 3.8+
- Django 3.2+
- Celery (for webhook-triggered sync tasks)
- A Squarelet OAuth application (key + secret)

---

## Installation

```bash
pip install squarelet_auth
```

---

## Setup

### 1. Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ...
    "social_django",
    "squarelet_auth",
    "squarelet_auth.organizations",
    "squarelet_auth.users",
]
```

### 2. Configure settings

```python
# Required
SOCIAL_AUTH_SQUARELET_KEY = "your-client-id"
SOCIAL_AUTH_SQUARELET_SECRET = "your-client-secret"
BASE_URL = "https://yourdomain.com"  # Used for webhook validation

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "squarelet_auth.backends.SquareletBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Social auth pipeline (order matters)
SOCIAL_AUTH_PIPELINE = [
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "squarelet_auth.pipeline.associate_by_uuid",   # find existing user by Squarelet UUID
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "squarelet_auth.pipeline.save_info",            # create/update SquareletProfile + orgs
    "squarelet_auth.pipeline.save_session_data",
]

# Login/logout URLs
LOGIN_URL = "/auth/login/squarelet/"
LOGIN_REDIRECT_URL = "/"
```

### 3. Add URL patterns

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path("auth/", include("social_django.urls", namespace="social")),
    path("squarelet/", include("squarelet_auth.urls")),
    path("squarelet/organizations/", include(
        "squarelet_auth.organizations.urls",
        namespace="squarelet_auth_organizations",
    )),
]
```

### 4. Run migrations

```bash
python manage.py migrate
```

---

## Optional Settings

| Setting | Default | Description |
|---|---|---|
| `SQUARELET_URL` | `"https://accounts.muckrock.com"` | Base URL of the Squarelet service |
| `SQUARELET_DISABLE_CREATE_AGENCY` | `True` | If `True`, agency (bot) users are never created locally |
| `SQUARELET_CREATE_USER` | `None` | Dotted path to a custom user factory callable (see below) |
| `SQUARELET_WHITELIST_VERIFIED_JOURNALISTS` | `False` | Restrict access to verified journalists only |
| `SQUARELET_BYPASS_RATE_LIMIT_SECRET` | `""` | Secret for bypassing rate limits |
| `SQUARELET_INTENT` | `""` | Intent string passed to Squarelet during OAuth |
| `SQUARELET_RESOURCE_FIELDS` | `{}` | Extra fields to expose from entitlement resources (see below) |

---

## Accessing Squarelet Data

All Squarelet-synced data lives on the `SquareletProfile` linked to the user:

```python
# Get profile
profile = request.user.squarelet_profile

# Profile fields
profile.uuid            # UUID matching Squarelet's identifier
profile.username        # Squarelet username
profile.email           # Squarelet email
profile.name            # Full name
profile.avatar_url      # Avatar URL
profile.bio             # Markdown bio
profile.email_verified  # bool
profile.email_failed    # bool — True if we failed to deliver email to this address
profile.use_autologin   # bool — user preference for autologin links

# Organization access
profile.organization            # Active SquareletOrganization
profile.individual_organization # The user's personal SquareletOrganization
profile.verified_journalist     # bool — member of any verified journalistic org

# All organizations the user belongs to (M2M, returns SquareletOrganization queryset)
request.user.squarelet_organizations.all()
request.user.squarelet_organizations.filter(individual=False)  # non-personal orgs

# Memberships (through table)
request.user.squarelet_memberships.filter(admin=True)  # orgs where user is admin
```

### `SquareletOrganization` fields

```python
org = profile.organization

org.uuid               # UUID
org.name               # Display name
org.slug               # URL slug
org.individual         # bool — True for personal orgs
org.private            # bool
org.verified_journalist # bool
org.avatar_url
org.card               # Last 4 digits + brand of card on file (display only)
org.entitlement        # FK to Entitlement
org.date_update        # Date when monthly resources refresh
org.payment_failed     # bool

org.display_name       # "Personal Account" for individual orgs, else org.name
org.has_member(user)   # bool
org.has_admin(user)    # bool
```

### Switching Active Organization

POST to the `activate` view to switch a user's active organization:

```html
<form method="post" action="{% url 'squarelet_auth_organizations:activate' %}">
    {% csrf_token %}
    <input type="hidden" name="organization" value="{{ org.pk }}">
    <input type="hidden" name="next" value="{{ request.path }}">
    <button type="submit">Switch to {{ org.display_name }}</button>
</form>
```

Or programmatically:

```python
# Set active org (raises ValueError if user is not a member)
request.user.squarelet_profile.organization = some_org
```

---

## Syncing with Your Own User Model

Subscribe to the `user_update` signal to copy Squarelet data onto your own User model whenever it syncs:

```python
# apps.py or signals.py
from squarelet_auth.users.utils import user_update

def sync_squarelet_data(sender, user, data, **kwargs):
    """Copy Squarelet fields onto our User model."""
    user.name = data.get("name", "")
    user.email = data.get("email", "")
    user.save(update_fields=["name", "email"])

user_update.connect(sync_squarelet_data)
```

The signal fires after every successful sync (OAuth login or webhook update). `data` is the raw payload from Squarelet.

---

## Custom User Creation

By default, when a new Squarelet user logs in and no local `User` exists, `squarelet_auth` calls `User.objects.create_user(username=..., email=...)`. To customize this:

```python
# settings.py
SQUARELET_CREATE_USER = "myapp.auth.create_squarelet_user"
```

```python
# myapp/auth.py
def create_squarelet_user(uuid, data):
    """
    Called when a new Squarelet user has no matching local User.

    Args:
        uuid: The Squarelet UUID (string)
        data: The full Squarelet response payload (dict)

    Returns:
        A saved User instance
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username=data.get("preferred_username", ""),
        email=data.get("email") or None,
        # set any other fields your model requires
    )
```

---

## Entitlement Resource Fields

If you use Squarelet's entitlement system to gate features by subscription plan, you can expose resource fields as properties on `Entitlement`:

```python
# settings.py
SQUARELET_RESOURCE_FIELDS = {
    "monthly_requests": 0,    # field name: default value
    "ai_credits": 0,
}
```

Then:

```python
org.entitlement.monthly_requests  # int from entitlement's resources JSON
org.entitlement.ai_credits
```

---

## Webhooks

Squarelet pushes updates to your app whenever user or organization data changes. Configure the webhook URL in your Squarelet OAuth application settings:

```
https://yourdomain.com/squarelet/webhook/
```

The webhook validates requests using an HMAC signature derived from `SOCIAL_AUTH_SQUARELET_SECRET`. On receipt, it fires a Celery task (`squarelet_auth.tasks.pull_data`) that fetches fresh data from the Squarelet API.

Webhooks only **update** existing records — they will never create a new user or organization that isn't already in your database. Users must log in via OAuth at least once before webhook syncs apply to them.

Make sure Celery is running:

```bash
celery -A myproject worker -l info
```

---

## Admin

`squarelet_auth` registers `SquareletProfileAdmin` and `SquareletOrganizationAdmin` automatically.

To add a read-only Squarelet data panel to your own `UserAdmin`:

```python
# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from squarelet_auth.users.admin import SquareletProfileInline
from myapp.models import User

@admin.register(User)
class MyUserAdmin(UserAdmin):
    inlines = [SquareletProfileInline]
```

---

## Universal Logout

Squarelet supports universal logout — when a user logs out of Squarelet, all connected apps are notified. To enable it, configure your Squarelet OAuth app with the logout URL:

```
https://yourdomain.com/squarelet/logout/
```

The `save_session_data` pipeline step stores `session_state` and `id_token` in the session, which are used by the logout endpoint to validate the logout request.

---

## Full Example: `settings.py`

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "social_django",
    "squarelet_auth",
    "squarelet_auth.organizations",
    "squarelet_auth.users",
    "myapp",
]

AUTHENTICATION_BACKENDS = [
    "squarelet_auth.backends.SquareletBackend",
    "django.contrib.auth.backends.ModelBackend",
]

SOCIAL_AUTH_PIPELINE = [
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "squarelet_auth.pipeline.associate_by_uuid",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "squarelet_auth.pipeline.save_info",
    "squarelet_auth.pipeline.save_session_data",
]

SOCIAL_AUTH_SQUARELET_KEY = env("SOCIAL_AUTH_SQUARELET_KEY")
SOCIAL_AUTH_SQUARELET_SECRET = env("SOCIAL_AUTH_SQUARELET_SECRET")
BASE_URL = env("BASE_URL")

LOGIN_URL = "/auth/login/squarelet/"
LOGIN_REDIRECT_URL = "/"
```
