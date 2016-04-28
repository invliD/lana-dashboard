# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-28 23:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lana_data', '0002_auto_20160428_1629'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='autonomoussystem',
            options={'verbose_name': 'Autonomous System', 'verbose_name_plural': 'Autonomous Systems'},
        ),
        migrations.AlterModelOptions(
            name='institution',
            options={'verbose_name': 'Institution', 'verbose_name_plural': 'Institutions'},
        ),
        migrations.AlterModelOptions(
            name='ipv4subnet',
            options={'verbose_name': 'IPv4 Subnet', 'verbose_name_plural': 'IPv4 Subnets'},
        ),
        migrations.AlterField(
            model_name='autonomoussystem',
            name='as_number',
            field=models.IntegerField(primary_key=True, serialize=False, verbose_name='AS Number'),
        ),
        migrations.AlterField(
            model_name='autonomoussystem',
            name='comment',
            field=models.CharField(max_length=255, verbose_name='Comment'),
        ),
        migrations.AlterField(
            model_name='autonomoussystem',
            name='fqdn',
            field=models.CharField(max_length=255, verbose_name='FQDN'),
        ),
        migrations.AlterField(
            model_name='autonomoussystem',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='autonomous_systems', to='lana_data.Institution', verbose_name='Institution'),
        ),
        migrations.AlterField(
            model_name='institution',
            name='code',
            field=models.CharField(max_length=8, unique=True, verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='institution',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='institution',
            name='owners',
            field=models.ManyToManyField(related_name='institutions', to=settings.AUTH_USER_MODEL, verbose_name='Managers'),
        ),
        migrations.AlterField(
            model_name='ipv4subnet',
            name='comment',
            field=models.CharField(max_length=255, verbose_name='Comment'),
        ),
        migrations.AlterField(
            model_name='ipv4subnet',
            name='dns_server',
            field=models.GenericIPAddressField(protocol='IPv4', verbose_name='DNS Server'),
        ),
        migrations.AlterField(
            model_name='ipv4subnet',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ipv4_subnets', to='lana_data.Institution', verbose_name='Institution'),
        ),
        migrations.AlterField(
            model_name='ipv4subnet',
            name='network_address',
            field=models.GenericIPAddressField(protocol='IPv4', verbose_name='Network Address'),
        ),
        migrations.AlterField(
            model_name='ipv4subnet',
            name='subnet_bits',
            field=models.IntegerField(verbose_name='Subnet Bits'),
        ),
    ]
