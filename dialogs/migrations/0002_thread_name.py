# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-04 11:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialogs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='name',
            field=models.TextField(default='No name'),
        ),
    ]