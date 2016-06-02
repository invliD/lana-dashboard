# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lana_data', '0004_release'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='abuse_email',
            field=models.EmailField(default='abuse@example.com', max_length=254, verbose_name='Abuse Email'),
            preserve_default=False,
        ),
    ]
