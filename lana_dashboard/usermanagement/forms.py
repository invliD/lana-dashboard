from django import forms
from django.utils.translation import ugettext_lazy as _

from lana_dashboard.usermanagement.models import ContactInformation


class ContactInformationForm(forms.ModelForm):
	email = forms.EmailField(label=_('Email address'))

	class Meta:
		model = ContactInformation
		fields = ['email', 'show_email', 'skype_user', 'xmpp_address', 'pgp_key', 'additional_text']
