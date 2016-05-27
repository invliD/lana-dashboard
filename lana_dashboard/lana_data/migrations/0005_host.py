# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def forward_func(apps, schema_editor):
    AutonomousSystem = apps.get_model('lana_data', 'AutonomousSystem')
    Host = apps.get_model('lana_data', 'Host')
    TunnelEndpoint = apps.get_model('lana_data', 'TunnelEndpoint')

    autonomous_systems = AutonomousSystem.objects.all()
    for autonomous_system in autonomous_systems:
        host = Host(fqdn=autonomous_system.fqdn, autonomous_system=autonomous_system)
        host.save()

    tunnel_endpoints = TunnelEndpoint.objects.all()
    for tunnel_endpoint in tunnel_endpoints:
        host = tunnel_endpoint.autonomous_system.hosts.all()[0]
        tunnel_endpoint.host = host
        tunnel_endpoint.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lana_data', '0004_private'),
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fqdn', models.CharField(max_length=255, unique=True, verbose_name='FQDN')),
                ('autonomous_system', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='hosts', to='lana_data.AutonomousSystem', verbose_name='Autonomous System')),
            ],
            options={
                'verbose_name_plural': 'Hosts',
                'verbose_name': 'Host',
                'ordering': ['fqdn'],
            },
        ),
        migrations.AddField(
            model_name='tunnelendpoint',
            name='host',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='tunnel_endpoints', to='lana_data.Host', verbose_name='Host'),
        ),
        migrations.RunPython(forward_func),
        migrations.AlterField(
            model_name='tunnelendpoint',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='tunnel_endpoints', to='lana_data.Host', verbose_name='Host'),
        ),
        migrations.AlterModelOptions(
            name='tunnel',
            options={'ordering': ['endpoint1__host__autonomous_system__as_number', 'endpoint2__host__autonomous_system__as_number']},
        ),
        migrations.RemoveField(
            model_name='autonomoussystem',
            name='fqdn',
        ),
        migrations.RemoveField(
            model_name='tunnelendpoint',
            name='autonomous_system',
        ),
    ]
