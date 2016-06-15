# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.postgres.fields.ranges
from django.db import migrations, models
import netfields.fields


def forward_func(apps, schema_editor):
    Host = apps.get_model('lana_data', 'Host')

    hosts = Host.objects.all()
    for host in hosts:
        endpoints = host.tunnel_endpoints.all()
        if len(endpoints) > 0:
            common_external_hostname = None
            common_external_ipv4 = None
            common_tunnel_ipv4 = None

            for endpoint in endpoints:
                if common_external_hostname != -1 and endpoint.external_hostname != '' and endpoint.external_hostname is not None:
                    if common_external_hostname is None:
                        common_external_hostname = endpoint.external_hostname
                    elif common_external_hostname != endpoint.external_hostname:
                        common_external_hostname = -1
                if common_external_ipv4 != -1:
                    if common_external_ipv4 is None:
                        common_external_ipv4 = endpoint.external_ipv4
                    elif endpoint.external_ipv4 is not None and common_external_ipv4 != endpoint.external_ipv4:
                        common_external_ipv4 = -1
                if common_tunnel_ipv4 != -1:
                    if common_tunnel_ipv4 is None:
                        common_tunnel_ipv4 = endpoint.internal_ipv4
                    elif endpoint.internal_ipv4 is not None and common_tunnel_ipv4 != endpoint.internal_ipv4:
                        common_tunnel_ipv4 = -1

            if common_external_hostname is not None and common_external_hostname != -1:
                host.external_hostname = common_external_hostname
            if common_external_ipv4 is not None and common_external_ipv4 != -1:
                host.external_ipv4 = common_external_ipv4
            if common_tunnel_ipv4 is not None and common_tunnel_ipv4 != -1:
                host.tunnel_ipv4 = common_tunnel_ipv4
                endpoints.update(internal_ipv4='')
            host.save()


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
        migrations.AddField(
            model_name='host',
            name='external_hostname',
            field=models.CharField(blank=True, max_length=255, verbose_name='External hostname'),
        ),
        migrations.AddField(
            model_name='host',
            name='external_ipv4',
            field=netfields.fields.InetAddressField(blank=True, max_length=39, null=True, verbose_name='External IPv4 address'),
        ),
        migrations.AddField(
            model_name='host',
            name='internal_ipv4',
            field=netfields.fields.InetAddressField(blank=True, max_length=39, null=True, verbose_name='Internal IPv4 address'),
        ),
        migrations.AddField(
            model_name='host',
            name='tunnel_ipv4',
            field=netfields.fields.InetAddressField(blank=True, max_length=39, null=True, verbose_name='Tunnel IPv4 address'),
        ),
        migrations.RunPython(forward_func),
        migrations.RemoveField(
            model_name='tunnelendpoint',
            name='external_hostname',
        ),
        migrations.RemoveField(
            model_name='tunnelendpoint',
            name='external_ipv4',
        ),
        migrations.RenameField(
            model_name='tunnelendpoint',
            old_name='internal_ipv4',
            new_name='override_internal_ipv4',
        ),
        migrations.AlterField(
            model_name='tunnelendpoint',
            name='override_internal_ipv4',
            field=netfields.fields.InetAddressField(blank=True, max_length=39, null=True, verbose_name='Override internal IPv4 address'),
        ),
        migrations.AddField(
            model_name='institution',
            name='as_range',
            field=django.contrib.postgres.fields.ranges.BigIntegerRangeField(blank=True, null=True, verbose_name='AS Range'),
        ),
    ]
