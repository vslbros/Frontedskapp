# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-17 09:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontdeskapp', '0012_auto_20180217_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomdetails',
            name='room_type',
            field=models.CharField(max_length=50),
        ),
    ]