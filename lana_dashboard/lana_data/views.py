from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from lana_dashboard.lana_data.forms import InstitutionForm

from lana_dashboard.lana_data.models import AutonomousSystem, Institution, IPv4Subnet


def list_institutions(request):
	institutions = Institution.objects.all()

	return render(request, 'institutions_list.html', {
		'header_active': 'institutions',
		'institutions': institutions,
	})


def create_institution(request):
	if request.method == 'POST':
		form = InstitutionForm(data=request.POST)
		if form.is_valid():
			institution = form.instance
			institution.save()
			institution.owners.add(request.user)
			institution.save()
			return HttpResponseRedirect(reverse('lana_data:institution-details', kwargs={'code': institution.code}))
	else:
		form = InstitutionForm()

	form.helper = FormHelper()
	form.helper.form_class = 'form-horizontal'
	form.helper.label_class = 'col-md-2'
	form.helper.field_class = 'col-md-4'
	form.helper.html5_required = True
	form.helper.add_input(Submit("submit", "Create"))

	return render(request, 'institutions_create.html', {
		'header_active': 'institutions',
		'form': form,
	})


def show_institution(request, code=None):
	institution = Institution.objects.get(code=code)

	return render(request, 'institutions_details.html', {
		'header_active': 'institutions',
		'institution': institution,
	})


def list_autonomous_systems(request):
	autonomous_systems = AutonomousSystem.objects.all()

	return render(request, 'autonomous_systems_list.html', {
		'header_active': 'autonomous_systems',
		'autonomous_systems': autonomous_systems,
	})


def list_ipv4(request):
	subnets = IPv4Subnet.objects.all()

	return render(request, 'ipv4_list.html', {
		'header_active': 'ipv4',
		'subnets': subnets,
	})
