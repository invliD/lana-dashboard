from django.forms import ModelForm, NumberInput

from lana_dashboard.lana_data.models import AutonomousSystem, Institution, IPv4Subnet


class InstitutionForm(ModelForm):
	class Meta:
		model = Institution
		fields = ['code', 'name', 'owners']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['owners'].required = False


class AutonomousSystemForm(ModelForm):
	class Meta:
		model = AutonomousSystem
		fields = ['as_number', 'fqdn', 'comment', 'institution']
		widgets = {
			'as_number': NumberInput(attrs={'min': 0, 'max': 4294967296}),
		}


class IPv4SubnetForm(ModelForm):
	class Meta:
		model = IPv4Subnet
		fields = ['network_address', 'subnet_bits', 'dns_server', 'comment', 'institution']
		widgets = {
			'subnet_bits': NumberInput(attrs={'min': 0, 'max': 32}),
		}
