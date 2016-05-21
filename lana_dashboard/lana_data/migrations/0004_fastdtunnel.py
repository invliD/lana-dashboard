# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def forward_func(apps, schema_editor):
    FastdTunnel = apps.get_model('lana_data', 'FastdTunnel')
    Tunnel = apps.get_model('lana_data', 'Tunnel')

    fastd_tunnels = Tunnel.objects.filter(protocol='fastd')
    for tunnel in fastd_tunnels:
        fastd = FastdTunnel(tunnel_ptr=tunnel)
        fastd.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lana_data', '0003_tunnelendpoint_external_hostname'),
    ]

    operations = [
        migrations.CreateModel(
            name='FastdTunnel',
            fields=[
                ('tunnel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='lana_data.Tunnel')),
            ],
        ),
        migrations.RunPython(forward_func),
        migrations.RemoveField(
            model_name='tunnel',
            name='protocol',
        ),
    ]
