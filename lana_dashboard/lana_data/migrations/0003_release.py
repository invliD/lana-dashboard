# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def forward_func(apps, schema_editor):
    FastdTunnel = apps.get_model('lana_data', 'FastdTunnel')
    FastdTunnelEndpoint = apps.get_model('lana_data', 'FastdTunnelEndpoint')
    Tunnel = apps.get_model('lana_data', 'Tunnel')

    fastd_tunnels = Tunnel.objects.filter(protocol='fastd')
    for tunnel in fastd_tunnels:
        fastd = FastdTunnel(tunnel_ptr=tunnel)
        fastd.save()
        for endpoint in [tunnel.endpoint1, tunnel.endpoint2]:
            fastd_endpoint = FastdTunnelEndpoint(tunnelendpoint_ptr=endpoint)
            fastd_endpoint.port = endpoint.port
            fastd_endpoint.public_key = endpoint.public_key
            fastd_endpoint.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lana_data', '0002_release'),
    ]

    operations = [
        migrations.CreateModel(
            name='FastdTunnel',
            fields=[
                ('tunnel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lana_data.Tunnel')),
            ],
        ),
        migrations.CreateModel(
            name='FastdTunnelEndpoint',
            fields=[
                ('tunnelendpoint_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lana_data.TunnelEndpoint')),
                ('port', models.IntegerField(blank=True, help_text='Defaults to remote AS number if ≤ 65535.', null=True, verbose_name='Port')),
                ('public_key', models.CharField(blank=True, max_length=255, null=True, verbose_name='Public key')),
            ],
        ),
        migrations.RunPython(forward_func),
        migrations.CreateModel(
            name='VtunTunnel',
            fields=[
                ('tunnel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lana_data.Tunnel')),
                ('transport', models.CharField(choices=[('udp', 'udp'), ('tcp', 'tcp')], max_length=3, verbose_name='Transport protocol')),
                ('compression', models.CharField(blank=True, max_length=255, null=True, verbose_name='Compression')),
            ],
        ),
        migrations.CreateModel(
            name='VtunTunnelEndpoint',
            fields=[
                ('tunnelendpoint_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lana_data.TunnelEndpoint')),
                ('port', models.IntegerField(blank=True, null=True, verbose_name='Port')),
            ],
        ),
        migrations.RemoveField(
            model_name='tunnel',
            name='protocol',
        ),
        migrations.RemoveField(
            model_name='tunnelendpoint',
            name='port',
        ),
        migrations.RemoveField(
            model_name='tunnelendpoint',
            name='public_key',
        ),
        migrations.AddField(
            model_name='tunnelendpoint',
            name='external_hostname',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='External hostname'),
        ),
    ]
