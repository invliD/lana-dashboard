# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-16 17:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lana_data', '0008_institution_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='tunnelendpoint',
            name='port',
            field=models.IntegerField(blank=True, help_text='Defaults to remote AS number if ≤ 65535 (Fastd only).', null=True, verbose_name='Port'),
        ),
    ]
