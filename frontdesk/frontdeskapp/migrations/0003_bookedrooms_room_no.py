# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-17 07:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontdeskapp', '0002_auto_20180217_0609'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookedrooms',
            name='room_no',
            field=models.IntegerField(null=True, verbose_name='Room No.'),
        ),
    ]
