# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-22 05:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontdeskapp', '0015_auto_20180222_0412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billing',
            name='amount',
            field=models.IntegerField(blank=True, verbose_name='Amount'),
        ),
        migrations.AlterField(
            model_name='billing',
            name='paid',
            field=models.CharField(blank=True, max_length=3),
        ),
    ]
