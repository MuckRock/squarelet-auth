# Generated by Django 2.0.8 on 2020-05-27 16:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('squarelet_auth_organizations', '0005_auto_20200527_0921'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='plan',
        ),
        migrations.DeleteModel(
            name='Plan',
        ),
    ]
