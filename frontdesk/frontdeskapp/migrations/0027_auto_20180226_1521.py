# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-26 15:21
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontdeskapp', '0026_auto_20180226_0811'),
    ]

    operations = [
        migrations.AddField(
            model_name='billing',
            name='biling_date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='bookedrooms',
            name='booking_date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='bookedrooms',
            name='departure_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 2, 27, 15, 21, 9, 446784)),
        ),
    ]
