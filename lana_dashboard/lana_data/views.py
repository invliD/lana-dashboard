from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from lana_dashboard.lana_data.forms import InstitutionForm

from lana_dashboard.lana_data.models import AutonomousSystem, Institution, IPv4Subnet


@login_required
def list_institutions(request):
	institutions = Institution.objects.all()

	return render(request, 'institutions_list.html', {
		'header_active': 'institutions',
		'institutions': institutions,
	})


@login_required
def edit_institution(request, code=None):
	if code:
		mode = 'edit'
		institution = get_object_or_404(Institution, code=code)
		if not institution.can_edit(request.user):
			raise PermissionDenied
	else:
		mode = 'create'
		institution = Institution()

	if request.method == 'POST':
		form = InstitutionForm(instance=institution, data=request.POST)
		if form.is_valid():
			institution = form.instance
			if mode == 'create':
				institution.save()
				institution.owners.add(request.user)
			institution.save()
			return HttpResponseRedirect(reverse('lana_data:institution-details', kwargs={'code': institution.code}))
	else:
		form = InstitutionForm(instance=institution)

	form.helper = FormHelper()
	form.helper.form_class = 'form-horizontal'
	form.helper.label_class = 'col-md-2'
	form.helper.field_class = 'col-md-4'
	form.helper.html5_required = True
	if mode == 'create':
		form.helper.add_input(Submit("submit", "Create"))
	else:
		form.helper.add_input(Submit("submit", "Save"))

	return render(request, 'institutions_edit.html', {
		'header_active': 'institutions',
		'mode': mode,
		'form': form,
	})


@login_required
def show_institution(request, code=None):
	institution = get_object_or_404(Institution, code=code)

	return render(request, 'institutions_details.html', {
		'header_active': 'institutions',
		'institution': institution,
		'can_edit': institution.can_edit(request.user),
	})


@login_required
def list_autonomous_systems(request):
	autonomous_systems = AutonomousSystem.objects.all()

	return render(request, 'autonomous_systems_list.html', {
		'header_active': 'autonomous_systems',
		'autonomous_systems': autonomous_systems,
	})


@login_required
def list_ipv4(request):
	subnets = IPv4Subnet.objects.all()

	return render(request, 'ipv4_list.html', {
		'header_active': 'ipv4',
		'subnets': subnets,
	})
