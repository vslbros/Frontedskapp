# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-17 09:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontdeskapp', '0009_resources_resource_qty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resources',
            name='price',
            field=models.IntegerField(blank=True, verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='resources',
            name='resource_qty',
            field=models.IntegerField(blank=True, null=True, verbose_name='Resource Qty'),
        ),
    ]
