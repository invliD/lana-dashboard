# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-16 17:44
from __future__ import unicode_literals

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lana_data', '0007_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='color',
            field=colorfield.fields.ColorField(default='#808080', max_length=10, verbose_name='Institution Color'),
        ),
    ]