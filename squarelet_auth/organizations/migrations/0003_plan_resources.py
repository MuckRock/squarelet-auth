# Generated by Django 2.0.8 on 2020-05-26 08:52

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('squarelet_auth_organizations', '0002_auto_20200423_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='resources',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]
