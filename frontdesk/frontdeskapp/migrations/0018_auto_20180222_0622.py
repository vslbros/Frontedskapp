# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-22 06:22
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontdeskapp', '0017_auto_20180222_0620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookedrooms',
            name='departure_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 2, 23, 6, 22, 10, 714144)),
        ),
    ]
