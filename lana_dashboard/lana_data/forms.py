from django.forms import ModelForm

from lana_dashboard.lana_data.models import Institution


class InstitutionForm(ModelForm):
	class Meta:
		model = Institution
		fields = ['code', 'name']
