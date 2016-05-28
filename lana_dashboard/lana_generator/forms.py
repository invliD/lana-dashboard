from django import forms


class FastdGeneratorForm(forms.Form):
	tunnel_name = forms.CharField(max_length=32)
