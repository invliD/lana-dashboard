# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forward_func(apps, schema_editor):
	AutonomousSystem = apps.get_model('lana_data', 'AutonomousSystem')
	autonomous_systems = AutonomousSystem.objects.all().order_by('as_number')

	i = 1
	for autonomous_system in autonomous_systems:
		autonomous_system.id = i
		autonomous_system.save()
		i += 1


class Migration(migrations.Migration):

	dependencies = [
		('lana_data', '0005_auto_20160429_1626'),
		]

	operations = [
		migrations.AddField(
			model_name='autonomoussystem',
			name='id',
			field=models.IntegerField(auto_created=True, blank=True, null=True, default=None, verbose_name='ID')
			),
		migrations.RunPython(forward_func),
		migrations.AlterField(
			model_name='autonomoussystem',
			name='id',
			field=models.AutoField(auto_created=True, serialize=False, verbose_name='ID'),
			),
		migrations.AlterField(
			model_name='autonomoussystem',
			name='as_number',
			field=models.BigIntegerField(unique=True, verbose_name='AS Number'),
			),
		migrations.AlterField(
			model_name='autonomoussystem',
			name='id',
			field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
			),
		]
