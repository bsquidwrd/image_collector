# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 00:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image_collector', '0023_credential_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='credential',
            name='client_secret',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]