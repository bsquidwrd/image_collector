# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 00:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image_collector', '0024_credential_client_secret'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credential',
            name='name',
            field=models.CharField(default='Blahhh', max_length=255),
            preserve_default=False,
        ),
    ]