from rest_framework.serializers import ModelSerializer, SerializerMethodField, SlugRelatedField

from lana_dashboard.lana_data.models import (
	AutonomousSystem,
	FastdTunnel,
	FastdTunnelEndpoint,
	Host,
	Institution,
	IPv4Subnet,
	Peering,
	Tunnel,
	TunnelEndpoint,
	VtunTunnel,
	VtunTunnelEndpoint,
)


class InstitutionSerializer(ModelSerializer):
	class Meta:
		model = Institution
		fields = ['name', 'code', 'abuse_email']


class AutonomousSystemSerializer(ModelSerializer):
	institution = SlugRelatedField(slug_field='code', read_only=True)

	class Meta:
		model = AutonomousSystem
		fields = ['as_number', 'institution']


class HostSerializer(ModelSerializer):
	autonomous_system = AutonomousSystemSerializer()
	external_hostname = SerializerMethodField()
	external_ipv4 = SerializerMethodField()
	internal_ipv4 = SerializerMethodField()

	class Meta:
		model = Host
		fields = ['fqdn', 'autonomous_system', 'external_hostname', 'external_ipv4', 'internal_ipv4']

	def get_external_hostname(self, obj):
		return obj.external_hostname if obj.external_hostname != '' else None

	def get_external_ipv4(self, obj):
		return str(obj.external_ipv4.ip) if obj.external_ipv4 is not None else None

	def get_internal_ipv4(self, obj):
		return str(obj.internal_ipv4.ip) if obj.internal_ipv4 is not None else None


class IPv4SubnetSerializer(ModelSerializer):
	institution = InstitutionSerializer()

	class Meta:
		model = IPv4Subnet
		fields = ['network', 'comment', 'institution']


class PeeringSerializer(ModelSerializer):
	class Meta:
		model = Peering
		fields = ['bfd_enabled']


class TunnelSerializer(ModelSerializer):
	class Meta:
		model = Tunnel
		fields = ['mode', 'encryption_method', 'mtu']


class FastdTunnelSerializer(TunnelSerializer):
	class Meta(TunnelSerializer.Meta):
		model = FastdTunnel


class VtunTunnelSerializer(TunnelSerializer):
	class Meta(TunnelSerializer.Meta):
		model = VtunTunnel
		fields = ['transport', 'mode', 'encryption_method', 'compression', 'mtu']


class TunnelEndpointSerializer(ModelSerializer):
	fqdn = SlugRelatedField(slug_field='fqdn', source='host', read_only=True)
	external_hostname = SerializerMethodField()
	external_ipv4 = SerializerMethodField()
	internal_ipv4 = SerializerMethodField()

	class Meta:
		model = TunnelEndpoint
		fields = ['fqdn', 'external_hostname', 'external_ipv4', 'internal_ipv4']

	def get_external_hostname(self, obj):
		return obj.host.external_hostname if obj.host.external_hostname != '' else None

	def get_external_ipv4(self, obj):
		return str(obj.host.external_ipv4.ip) if obj.host.external_ipv4 is not None else None

	def get_internal_ipv4(self, obj):
		if obj.tunnel.mode == Tunnel.MODE_TUN:
			return str(obj.internal_ipv4.ip) if obj.internal_ipv4 is not None else None
		else:
			return str(obj.internal_ipv4)


class FastdTunnelEndpointSerializer(TunnelEndpointSerializer):
	class Meta(TunnelEndpointSerializer.Meta):
		model = FastdTunnelEndpoint
		fields = ['fqdn', 'external_hostname', 'external_ipv4', 'internal_ipv4', 'port', 'public_key']


class VtunTunnelEndpointSerializer(TunnelEndpointSerializer):
	class Meta(TunnelEndpointSerializer.Meta):
		model = VtunTunnelEndpoint
		fields = ['fqdn', 'external_hostname', 'external_ipv4', 'internal_ipv4', 'port']
