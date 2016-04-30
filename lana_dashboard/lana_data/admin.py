from django.contrib import admin

from lana_dashboard.lana_data.models import AutonomousSystem, Institution, IPv4Subnet, Tunnel, TunnelEndpoint


class InstitutionAdmin(admin.ModelAdmin):
	list_display = ('name', 'code')


class AutonomousSystemAdmin(admin.ModelAdmin):
	list_display = ('as_number', 'fqdn', 'comment', 'institution')


class IPv4SubnetAdmin(admin.ModelAdmin):
	list_display = ('network_address', 'subnet_bits', 'dns_server', 'comment', 'institution')


class TunnelAdmin(admin.ModelAdmin):
	list_display = ('comment', 'endpoint1', 'endpoint2')


class TunnelEndpointAdmin(admin.ModelAdmin):
	list_display = ('autonomous_system',)


admin.site.register(Institution, InstitutionAdmin)
admin.site.register(AutonomousSystem, AutonomousSystemAdmin)
admin.site.register(IPv4Subnet, IPv4SubnetAdmin)
admin.site.register(Tunnel, TunnelAdmin)
admin.site.register(TunnelEndpoint, TunnelEndpointAdmin)
