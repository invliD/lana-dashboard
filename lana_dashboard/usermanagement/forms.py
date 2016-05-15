from django.forms import ModelForm

from lana_dashboard.usermanagement.models import ContactInformation


class ContactInformationForm(ModelForm):
	class Meta:
		model = ContactInformation
		fields = ['show_email', 'skype_user', 'xmpp_address', 'additional_text']
