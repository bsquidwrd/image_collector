# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-02 19:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('image_collector', '0026_auto_20160423_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]