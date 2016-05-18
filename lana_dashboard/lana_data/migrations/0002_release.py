# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import colorfield.fields
from django.db import migrations, models
import django.db.models.deletion
import netfields.fields


def forward_func(apps, schema_editor):
    IPv4Subnet = apps.get_model('lana_data', 'IPv4Subnet')
    subnets = IPv4Subnet.objects.all()
    for subnet in subnets:
        cidr = "{}/{}".format(subnet.network_address, subnet.subnet_bits)
        subnet.network = cidr
        subnet.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lana_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tunnel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protocol', models.CharField(choices=[('fastd', 'Fastd tunnel'), ('other', 'Other')], max_length=5, verbose_name='Protocol')),
                ('mode', models.CharField(choices=[('tun', 'tun'), ('tap', 'tap')], max_length=3, verbose_name='Mode')),
                ('comment', models.CharField(blank=True, max_length=255, null=True, verbose_name='Comment')),
                ('encryption_method', models.CharField(blank=True, max_length=255, null=True, verbose_name='Encryption method')),
                ('mtu', models.IntegerField(blank=True, null=True, verbose_name='MTU')),
            ],
            options={
                'ordering': ['endpoint1__autonomous_system__as_number', 'endpoint2__autonomous_system__as_number'],
            },
        ),
        migrations.CreateModel(
            name='TunnelEndpoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_ipv4', netfields.fields.InetAddressField(blank=True, max_length=39, null=True, verbose_name='External IPv4 address')),
                ('internal_ipv4', netfields.fields.InetAddressField(blank=True, max_length=39, null=True, verbose_name='Internal IPv4 address')),
                ('port', models.IntegerField(blank=True, help_text='Defaults to remote AS number if ≤ 65535 (Fastd only).', null=True, verbose_name='Port')),
                ('public_key', models.CharField(blank=True, max_length=255, null=True, verbose_name='Public key')),
            ],
        ),
        migrations.AlterModelOptions(
            name='autonomoussystem',
            options={'ordering': ['as_number'], 'verbose_name': 'Autonomous System', 'verbose_name_plural': 'Autonomous Systems'},
        ),
        migrations.AlterModelOptions(
            name='institution',
            options={'ordering': ['code'], 'verbose_name': 'Institution', 'verbose_name_plural': 'Institutions'},
        ),
        migrations.AlterModelOptions(
            name='ipv4subnet',
            options={'ordering': ['network'], 'verbose_name': 'IPv4 Subnet', 'verbose_name_plural': 'IPv4 Subnets'},
        ),
        migrations.AddField(
            model_name='autonomoussystem',
            name='location_lat',
            field=models.FloatField(blank=True, null=True, verbose_name='Latitude'),
        ),
        migrations.AddField(
            model_name='autonomoussystem',
            name='location_lng',
            field=models.FloatField(blank=True, null=True, verbose_name='Longitude'),
        ),
        migrations.AddField(
            model_name='institution',
            name='abuse_email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Abuse Email'),
        ),
        migrations.AddField(
            model_name='institution',
            name='color',
            field=colorfield.fields.ColorField(default='#808080', max_length=10, verbose_name='Institution Color'),
        ),
        migrations.AddField(
            model_name='ipv4subnet',
            name='network',
            field=netfields.fields.CidrAddressField(blank=True, max_length=43, null=True, unique=True, verbose_name='Network'),
        ),
        migrations.RunPython(forward_func),
        migrations.AlterField(
            model_name='ipv4subnet',
            name='network',
            field=netfields.fields.CidrAddressField(max_length=43, unique=True, verbose_name='Network'),
        ),
        migrations.AlterField(
            model_name='ipv4subnet',
            name='dns_server',
            field=netfields.fields.InetAddressField(blank=True, max_length=39, null=True, verbose_name='DNS Server'),
        ),
        migrations.AlterUniqueTogether(
            name='ipv4subnet',
            unique_together=set([]),
        ),
        migrations.AddField(
            model_name='tunnelendpoint',
            name='autonomous_system',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tunnel_endpoints', to='lana_data.AutonomousSystem', verbose_name='Autonomous System'),
        ),
        migrations.AddField(
            model_name='tunnel',
            name='endpoint1',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tunnel1', to='lana_data.TunnelEndpoint', verbose_name='Endpoint 1'),
        ),
        migrations.AddField(
            model_name='tunnel',
            name='endpoint2',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tunnel2', to='lana_data.TunnelEndpoint', verbose_name='Endpoint 2'),
        ),
        migrations.RemoveField(
            model_name='ipv4subnet',
            name='network_address',
        ),
        migrations.RemoveField(
            model_name='ipv4subnet',
            name='subnet_bits',
        ),
    ]
