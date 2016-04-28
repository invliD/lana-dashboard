from django.forms import ModelForm, NumberInput

from lana_dashboard.lana_data.models import AutonomousSystem, Institution


class InstitutionForm(ModelForm):
	class Meta:
		model = Institution
		fields = ['code', 'name']


class AutonomousSystemForm(ModelForm):

	class Meta:
		model = AutonomousSystem
		fields = ['as_number', 'fqdn', 'comment', 'institution']
		widgets = {
			'as_number': NumberInput(attrs={'min': 0, 'max': 4294967296})
		}
