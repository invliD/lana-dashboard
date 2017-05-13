from django.contrib import admin

from lana_dashboard.lana_data import models


@admin.register(models.Institution)
class InstitutionAdmin(admin.ModelAdmin):
	list_display = ('name', 'code')


@admin.register(models.AutonomousSystem)
class AutonomousSystemAdmin(admin.ModelAdmin):
	list_display = ('as_number', 'comment', 'institution')


@admin.register(models.Host)
class HostAdmin(admin.ModelAdmin):
	list_display = ('fqdn', 'comment', 'autonomous_system')


@admin.register(models.IPv4Subnet)
class IPv4SubnetAdmin(admin.ModelAdmin):
	list_display = ('network', 'dns_server', 'comment', 'institution')


@admin.register(models.TunnelPeering)
class TunnelPeeringAdmin(admin.ModelAdmin):
	list_display = ('tunnel', 'bfd_enabled')


@admin.register(models.Tunnel)
class TunnelAdmin(admin.ModelAdmin):
	list_display = ('comment', 'endpoint1', 'endpoint2')


@admin.register(models.FastdTunnel)
class FastdTunnelAdmin(TunnelAdmin):
	pass


@admin.register(models.VtunTunnel)
class VtunTunnelAdmin(TunnelAdmin):
	pass


@admin.register(models.TunnelEndpoint)
class TunnelEndpointAdmin(admin.ModelAdmin):
	list_display = ('host',)


@admin.register(models.FastdTunnelEndpoint)
class FastdTunnelEndpointAdmin(TunnelEndpointAdmin):
	list_display = ('host', 'port')


@admin.register(models.VtunTunnelEndpoint)
class VtunTunnelEndpointAdmin(TunnelEndpointAdmin):
	list_display = ('host', 'port')
