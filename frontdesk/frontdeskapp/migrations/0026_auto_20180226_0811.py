# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-26 08:11
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontdeskapp', '0025_auto_20180226_0810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookedrooms',
            name='departure_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 2, 27, 8, 11, 39, 960954)),
        ),
    ]
