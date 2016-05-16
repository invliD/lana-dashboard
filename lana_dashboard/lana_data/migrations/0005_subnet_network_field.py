# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import netfields


def forward_func(apps, schema_editor):
    IPv4Subnet = apps.get_model('lana_data', 'IPv4Subnet')
    subnets = IPv4Subnet.objects.all()
    for subnet in subnets:
        cidr = "{}/{}".format(subnet.network_address, subnet.subnet_bits)
        subnet.network = cidr
        subnet.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lana_data', '0004_institution_abuse_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='ipv4subnet',
            name='network',
            field=netfields.CidrAddressField(blank=True, max_length=43, null=True, unique=True, verbose_name='Network'),
        ),
        migrations.RunPython(forward_func),
        migrations.AlterField(
            model_name='ipv4subnet',
            name='network',
            field=netfields.CidrAddressField(max_length=43, unique=True, verbose_name='Network'),
        ),
        migrations.AlterUniqueTogether(
            name='ipv4subnet',
            unique_together=set([]),
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
