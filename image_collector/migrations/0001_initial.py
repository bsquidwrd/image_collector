# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-05 03:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Credential',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('api_key', models.CharField(max_length=255)),
                ('notes', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Extension',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('extension', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
                ('image_id', models.CharField(blank=True, default=None, max_length=255)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('video', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ImageUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('notes', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action', models.CharField(max_length=255)),
                ('result', models.CharField(blank=True, choices=[(2, 'fail'), (1, 'success'), (0, 'unknown')], max_length=255)),
                ('message', models.CharField(blank=True, max_length=255)),
                ('image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='log_image', to='image_collector.Image')),
            ],
        ),
        migrations.CreateModel(
            name='MimeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('mime', models.CharField(max_length=255)),
                ('extension', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image_collector.Extension')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('title', models.CharField(max_length=255)),
                ('url_name', models.CharField(max_length=255)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('permalink', models.URLField()),
                ('nsfw', models.BooleanField(default=False)),
                ('images', models.ManyToManyField(to='image_collector.Image')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_user', to='image_collector.ImageUser')),
            ],
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('url', models.URLField()),
                ('short_name', models.CharField(max_length=255)),
                ('notes', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='website',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_website', to='image_collector.Website'),
        ),
        migrations.AddField(
            model_name='log',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='log_post', to='image_collector.Post'),
        ),
        migrations.AddField(
            model_name='log',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='log_user', to='image_collector.ImageUser'),
        ),
        migrations.AddField(
            model_name='log',
            name='website',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='log_website', to='image_collector.Website'),
        ),
        migrations.AddField(
            model_name='imageuser',
            name='website',
            field=models.ManyToManyField(to='image_collector.Website'),
        ),
        migrations.AddField(
            model_name='image',
            name='mime_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='image_collector.MimeType'),
        ),
        migrations.AddField(
            model_name='image',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='image_user', to='image_collector.ImageUser'),
        ),
        migrations.AddField(
            model_name='credential',
            name='website',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image_collector.Website'),
        ),
    ]
