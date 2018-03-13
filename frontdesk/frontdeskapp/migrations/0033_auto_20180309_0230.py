# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-09 02:30
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontdeskapp', '0032_auto_20180226_2108'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee_details',
            name='leaves_allowed',
        ),
        migrations.RemoveField(
            model_name='employee_details',
            name='leaves_taken',
        ),
        migrations.AddField(
            model_name='eattendance_details',
            name='leave_date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='eattendance_details',
            name='reason',
            field=models.CharField(blank=True, default='Fever', max_length=50, null=True, verbose_name='Leave Reason'),
        ),
        migrations.AddField(
            model_name='employee_details',
            name='gross_salary',
            field=models.IntegerField(default=0, verbose_name='Gross Salary'),
        ),
        migrations.AddField(
            model_name='employee_details',
            name='leaves_available',
            field=models.IntegerField(default=0, verbose_name='Leaves Available'),
        ),
        migrations.AlterField(
            model_name='bookedrooms',
            name='departure_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 10, 2, 30, 24, 121479)),
        ),
    ]