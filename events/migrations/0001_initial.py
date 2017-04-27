# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-24 16:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_number', models.CharField(default='', max_length=10, unique=True)),
                ('title', models.CharField(default='', max_length=120)),
                ('date_submitted', models.CharField(default='', max_length=12)),
                ('status', models.CharField(default='', max_length=10)),
                ('date_last_edited', models.CharField(max_length=12)),
                ('submitters', models.CharField(max_length=120)),
                ('assignees', models.CharField(max_length=120)),
            ],
        ),
    ]