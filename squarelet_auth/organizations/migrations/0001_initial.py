from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Entitlement",
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
                    "name",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="name"
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        max_length=255, unique=True, verbose_name="slug"
                    ),
                ),
                ("description", models.TextField()),
                ("resources", models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name="SquareletOrganization",
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
                        editable=False,
                        help_text="Unique ID to link organizations across MuckRock's sites",
                        unique=True,
                        verbose_name="UUID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the organization",
                        max_length=255,
                        verbose_name="name",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="Unique slug for the organization which may be used in a URL",
                        max_length=255,
                        unique=True,
                        verbose_name="slug",
                    ),
                ),
                (
                    "private",
                    models.BooleanField(
                        default=False,
                        help_text="Whether or not to keep this organization and its membership list private",
                        verbose_name="private",
                    ),
                ),
                (
                    "individual",
                    models.BooleanField(
                        default=True,
                        help_text="Is this an organization for an individual user?",
                        verbose_name="individual",
                    ),
                ),
                (
                    "card",
                    models.CharField(
                        blank=True,
                        help_text="The brand and last 4 digits of the default credit card on file for this organization, for display purposes",
                        max_length=255,
                        verbose_name="card",
                    ),
                ),
                (
                    "avatar_url",
                    models.URLField(
                        blank=True,
                        help_text="A URL which points to an avatar for the organization",
                        max_length=255,
                        verbose_name="avatar url",
                    ),
                ),
                (
                    "date_update",
                    models.DateField(
                        help_text="The date when this organizations monthly resources will be refreshed",
                        null=True,
                        verbose_name="date update",
                    ),
                ),
                (
                    "payment_failed",
                    models.BooleanField(
                        default=False,
                        help_text="This organizations payment method has failed and should be updated",
                        verbose_name="payment failed",
                    ),
                ),
                (
                    "verified_journalist",
                    models.BooleanField(
                        default=False,
                        help_text="This organization is a verified journalistic organization",
                        verbose_name="verified journalist",
                    ),
                ),
                (
                    "entitlement",
                    models.ForeignKey(
                        help_text="The subscription type for this organization",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="squarelet_auth_organizations.entitlement",
                        verbose_name="entitlement",
                    ),
                ),
                (
                    "merged",
                    models.ForeignKey(
                        blank=True,
                        help_text="The organization this organization was merged in to",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="squarelet_auth_organizations.squareletorganization",
                    ),
                ),
            ],
            options={
                "ordering": ("slug",),
            },
        ),
        migrations.CreateModel(
            name="SquareletMembership",
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
                    "admin",
                    models.BooleanField(
                        default=False,
                        help_text="The user is an administrator for this organization",
                        verbose_name="admin",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        help_text="An organization being linked to a user",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="squarelet_memberships",
                        to="squarelet_auth_organizations.squareletorganization",
                        verbose_name="organization",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="A user being linked to an organization",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="squarelet_memberships",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="user",
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "organization")},
            },
        ),
        migrations.AddField(
            model_name="squareletorganization",
            name="users",
            field=models.ManyToManyField(
                help_text="The users who are members of this organization",
                related_name="squarelet_organizations",
                through="squarelet_auth_organizations.SquareletMembership",
                to=settings.AUTH_USER_MODEL,
                verbose_name="users",
            ),
        ),
    ]
