# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-06 03:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image_collector', '0008_auto_20160405_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='url_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
