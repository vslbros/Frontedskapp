# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-17 06:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontdeskapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerdetails',
            name='aadhar_ID',
            field=models.BigIntegerField(verbose_name='Adhaar'),
        ),
        migrations.AlterField(
            model_name='customerdetails',
            name='phone_no',
            field=models.BigIntegerField(verbose_name='Phone'),
        ),
        migrations.AlterField(
            model_name='employee_details',
            name='aadhar_ID',
            field=models.BigIntegerField(verbose_name='Aadhaar'),
        ),
        migrations.AlterField(
            model_name='employee_details',
            name='contact_no',
            field=models.BigIntegerField(verbose_name='Contact'),
        ),
    ]