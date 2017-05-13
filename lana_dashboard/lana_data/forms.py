from django.forms import ChoiceField, Form, ModelForm, NumberInput
from django.utils.translation import ugettext_lazy as _

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


class InstitutionForm(ModelForm):
	class Meta:
		model = Institution
		fields = ['code', 'name', 'as_range', 'color', 'abuse_email', 'owners']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['owners'].required = False


class AutonomousSystemForm(ModelForm):
	class Meta:
		model = AutonomousSystem
		fields = ['as_number', 'comment', 'institution', 'location_lat', 'location_lng', 'private']
		widgets = {
			'as_number': NumberInput(attrs={'min': 0, 'max': 4294967296}),
			'location_lat': NumberInput(attrs={'min': -90, 'max': 90}),
			'location_lng': NumberInput(attrs={'min': -180, 'max': 180}),
		}


class HostForm(ModelForm):
	class Meta:
		model = Host
		fields = ['fqdn', 'external_hostname', 'external_ipv4', 'internal_ipv4', 'tunnel_ipv4', 'comment', 'autonomous_system', 'private']


class PeeringForm(ModelForm):
	class Meta:
		model = Peering
		fields = ['bfd_enabled', 'private']


class TunnelProtocolForm(Form):
	protocol = ChoiceField(choices=(
		(None, '---------'),
		('fastd', _("Fastd tunnel")),
		('vtun', _("VTun tunnel")),
		('other', _("Other")),
	), required=False)


class IPv4SubnetForm(ModelForm):
	class Meta:
		model = IPv4Subnet
		fields = ['network', 'dns_server', 'comment', 'institution', 'private']
		widgets = {
			'subnet_bits': NumberInput(attrs={'min': 0, 'max': 32}),
		}


class TunnelForm(ModelForm):
	class Meta:
		model = Tunnel
		fields = ['mode', 'comment', 'encryption_method', 'mtu', 'private']


class FastdTunnelForm(TunnelForm):
	class Meta(TunnelForm.Meta):
		model = FastdTunnel


class VtunTunnelForm(TunnelForm):
	class Meta(TunnelForm.Meta):
		model = VtunTunnel
		fields = ['transport', 'mode', 'comment', 'encryption_method', 'compression', 'mtu', 'private']


class TunnelEndpointForm(ModelForm):
	class Meta:
		model = TunnelEndpoint
		fields = ['host', 'override_internal_ipv4', 'dynamic_ipv4']


class FastdTunnelEndpointForm(TunnelEndpointForm):
	class Meta(TunnelEndpointForm.Meta):
		model = FastdTunnelEndpoint
		fields = ['host', 'override_internal_ipv4', 'dynamic_ipv4', 'port', 'public_key']
		widgets = {
			'port': NumberInput(attrs={'min': 1, 'max': 65535}),
		}


class VtunTunnelEndpointForm(TunnelEndpointForm):
	class Meta(TunnelEndpointForm.Meta):
		model = VtunTunnelEndpoint
		fields = ['host', 'override_internal_ipv4', 'dynamic_ipv4', 'port']
		widgets = {
			'port': NumberInput(attrs={'min': 1, 'max': 65535}),
		}
