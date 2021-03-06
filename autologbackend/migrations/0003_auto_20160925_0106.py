# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-25 01:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autologbackend', '0002_vehicle_mileage_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='build_year',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='trip',
            name='arrival_time',
            field=models.DateTimeField(verbose_name='time of arrival'),
        ),
    ]
