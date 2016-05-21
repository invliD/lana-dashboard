# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def forward_func(apps, schema_editor):
    FastdTunnelEndpoint = apps.get_model('lana_data', 'FastdTunnelEndpoint')
    Tunnel = apps.get_model('lana_data', 'Tunnel')

    tunnels = Tunnel.objects.all()
    for tunnel in tunnels:
        if not hasattr(tunnel, 'fastdtunnel'):
            continue
        for endpoint in [tunnel.endpoint1, tunnel.endpoint2]:
            fastd_endpoint = FastdTunnelEndpoint(tunnelendpoint_ptr=endpoint)
            fastd_endpoint.port = endpoint.port
            fastd_endpoint.public_key = endpoint.public_key
            fastd_endpoint.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lana_data', '0004_fastdtunnel'),
    ]

    operations = [
        migrations.CreateModel(
            name='FastdTunnelEndpoint',
            fields=[
                ('tunnelendpoint_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lana_data.TunnelEndpoint')),
                ('port', models.IntegerField(blank=True, null=True, verbose_name='Port')),
                ('public_key', models.CharField(blank=True, max_length=255, null=True, verbose_name='Public key')),
            ],
        ),
        migrations.RunPython(forward_func),
        migrations.RemoveField(
            model_name='tunnelendpoint',
            name='port',
        ),
        migrations.RemoveField(
            model_name='tunnelendpoint',
            name='public_key',
        ),
    ]
