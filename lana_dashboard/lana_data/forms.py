from django.forms import ModelForm, NumberInput

from lana_dashboard.lana_data.models import AutonomousSystem, Institution, IPv4Subnet, Tunnel, TunnelEndpoint


class InstitutionForm(ModelForm):
	class Meta:
		model = Institution
		fields = ['code', 'name', 'color', 'abuse_email', 'owners']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['owners'].required = False


class AutonomousSystemForm(ModelForm):
	class Meta:
		model = AutonomousSystem
		fields = ['as_number', 'fqdn', 'comment', 'institution', 'location_lat', 'location_lng']
		widgets = {
			'as_number': NumberInput(attrs={'min': 0, 'max': 4294967296}),
			'location_lat': NumberInput(attrs={'min': -90, 'max': 90}),
			'location_lng': NumberInput(attrs={'min': -180, 'max': 180}),
		}


class IPv4SubnetForm(ModelForm):
	class Meta:
		model = IPv4Subnet
		fields = ['network', 'dns_server', 'comment', 'institution']
		widgets = {
			'subnet_bits': NumberInput(attrs={'min': 0, 'max': 32}),
		}


class TunnelForm(ModelForm):
	class Meta:
		model = Tunnel
		fields = ['protocol', 'mode', 'comment', 'encryption_method', 'mtu']


class TunnelEndpointForm(ModelForm):
	class Meta:
		model = TunnelEndpoint
		fields = ['autonomous_system', 'external_ipv4', 'internal_ipv4', 'public_key']
