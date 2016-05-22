from django.contrib import admin

from lana_dashboard.lana_data.models import (
	AutonomousSystem,
	FastdTunnel,
	FastdTunnelEndpoint,
	Institution,
	IPv4Subnet,
	Tunnel,
	TunnelEndpoint,
	VtunTunnel,
	VtunTunnelEndpoint,
)


class InstitutionAdmin(admin.ModelAdmin):
	list_display = ('name', 'code')


class AutonomousSystemAdmin(admin.ModelAdmin):
	list_display = ('as_number', 'fqdn', 'comment', 'institution')


class IPv4SubnetAdmin(admin.ModelAdmin):
	list_display = ('network', 'dns_server', 'comment', 'institution')


class TunnelAdmin(admin.ModelAdmin):
	list_display = ('comment', 'endpoint1', 'endpoint2')


class FastdTunnelAdmin(TunnelAdmin):
	pass


class VtunTunnelAdmin(TunnelAdmin):
	pass


class TunnelEndpointAdmin(admin.ModelAdmin):
	list_display = ('autonomous_system',)


class FastdTunnelEndpointAdmin(TunnelEndpointAdmin):
	list_display = ('autonomous_system', 'port')


class VtunTunnelEndpointAdmin(TunnelEndpointAdmin):
	list_display = ('autonomous_system', 'port')


admin.site.register(Institution, InstitutionAdmin)
admin.site.register(AutonomousSystem, AutonomousSystemAdmin)
admin.site.register(IPv4Subnet, IPv4SubnetAdmin)
admin.site.register(Tunnel, TunnelAdmin)
admin.site.register(FastdTunnel, FastdTunnelAdmin)
admin.site.register(VtunTunnel, VtunTunnelAdmin)
admin.site.register(TunnelEndpoint, TunnelEndpointAdmin)
admin.site.register(FastdTunnelEndpoint, FastdTunnelEndpointAdmin)
admin.site.register(VtunTunnelEndpoint, VtunTunnelEndpointAdmin)
