# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-12 00:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('image_collector', '0017_storage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storage',
            name='name',
        ),
        migrations.AddField(
            model_name='storage',
            name='credential',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to='image_collector.Credential'),
            preserve_default=False,
        ),
    ]
