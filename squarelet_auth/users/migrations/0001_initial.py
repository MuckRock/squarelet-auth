from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import squarelet_auth.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("squarelet_auth_organizations", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SquareletProfile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        help_text="Unique ID to link users across MuckRock's sites",
                        unique=True,
                        verbose_name="UUID",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        help_text="A unique public identifier for the user",
                        max_length=150,
                        unique=True,
                        verbose_name="username",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        help_text="The user's primary email address",
                        max_length=254,
                        null=True,
                        unique=True,
                        verbose_name="email",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        help_text="The user's full name",
                        max_length=255,
                        verbose_name="full name",
                    ),
                ),
                (
                    "avatar_url",
                    models.URLField(
                        blank=True,
                        help_text="A URL which points to an avatar for the user",
                        max_length=255,
                        verbose_name="avatar url",
                    ),
                ),
                (
                    "bio",
                    models.TextField(
                        blank=True,
                        help_text="Public bio for the user, in Markdown",
                        verbose_name="bio",
                    ),
                ),
                (
                    "email_failed",
                    models.BooleanField(
                        default=False,
                        help_text="Has an email we sent to this user's email address failed?",
                        verbose_name="email failed",
                    ),
                ),
                (
                    "email_verified",
                    models.BooleanField(
                        default=False,
                        help_text="Has this user's email address been verified?",
                        verbose_name="email verified",
                    ),
                ),
                (
                    "use_autologin",
                    models.BooleanField(
                        default=True,
                        help_text="Links you receive in emails from us will contain a token to automatically log you in",
                        verbose_name="use autologin",
                    ),
                ),
                (
                    "created_at",
                    squarelet_auth.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        help_text="Timestamp of when the profile was created",
                        verbose_name="created at",
                    ),
                ),
                (
                    "updated_at",
                    squarelet_auth.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        help_text="Timestamp of when the profile was last updated",
                        verbose_name="updated at",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        help_text="The user this profile belongs to",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="squarelet_profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="user",
                    ),
                ),
            ],
            options={
                "ordering": ("username",),
            },
        ),
    ]
