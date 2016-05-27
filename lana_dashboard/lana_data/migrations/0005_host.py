# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def forward_func(apps, schema_editor):
    AutonomousSystem = apps.get_model('lana_data', 'AutonomousSystem')
    Host = apps.get_model('lana_data', 'Host')

    autonomous_systems = AutonomousSystem.objects.all()
    for autonomous_system in autonomous_systems:
        host = Host(fqdn=autonomous_system.fqdn, autonomous_system=autonomous_system)
        host.save()


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
        migrations.RunPython(forward_func),
        migrations.RemoveField(
            model_name='autonomoussystem',
            name='fqdn',
        ),
    ]
