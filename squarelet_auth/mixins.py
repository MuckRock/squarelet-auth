# Django
from django.contrib.auth import login

# Third Party
import requests

# SquareletAuth
from squarelet_auth.users.utils import squarelet_update_or_create
from squarelet_auth.utils import squarelet_post


class MiniregMixin:
    """A mixin to expose miniregister functionality to a view"""

    minireg_source = "Default"
    field_map = {}

    def _create_squarelet_user(self, form, data):
        """Create a corresponding user on squarelet"""

        generic_error = (
            "Sorry, something went wrong with the user service.  "
            "Please try again later"
        )

        try:
            resp = squarelet_post("/api/users/", data=data)
        except requests.exceptions.RequestException:
            form.add_error(None, generic_error)
            raise
        if resp.status_code / 100 != 2:
            try:
                error_json = resp.json()
            except ValueError:
                form.add_error(None, generic_error)
            else:
                for field, errors in error_json.iteritems():
                    for error in errors:
                        form.add_error(self.field_map.get(field, field), error)
            finally:
                resp.raise_for_status()
        return resp.json()

    def miniregister(self, form, full_name, email):
        """Create a new user from their full name and email"""
        full_name = full_name.strip()

        user_json = self._create_squarelet_user(
            form, {"name": full_name, "preferred_username": full_name, "email": email}
        )

        user, _ = squarelet_update_or_create(user_json["uuid"], user_json)
        login(self.request, user, backend="squarelet_auth.backends.SquareletBackend")

        return user
