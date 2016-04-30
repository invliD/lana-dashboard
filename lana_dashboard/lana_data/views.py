from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from lana_dashboard.lana_data.forms import AutonomousSystemForm, InstitutionForm, IPv4SubnetForm

from lana_dashboard.lana_data.models import AutonomousSystem, Institution, IPv4Subnet


@login_required
def list_institutions(request):
	institutions = Institution.objects.all().order_by('code')

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

	# model.is_valid() modifies model. :(
	original = {
		'code': institution.code,
		'name': institution.name,
	}

	if request.method == 'POST':
		form = InstitutionForm(instance=institution, data=request.POST)
		if form.is_valid():
			institution = form.save(commit=False)
			institution.save()
			form.save_m2m()

			institution.owners.add(request.user)
			institution.save()
			return HttpResponseRedirect(reverse('lana_data:institution-details', kwargs={'code': institution.code}))
	else:
		form = InstitutionForm(instance=institution)

	form.fields['owners'].queryset = get_user_model().objects.filter(~Q(id=request.user.id)).order_by('last_name', 'first_name')

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
		'original': original,
		'form': form,
	})


@login_required
def show_institution(request, code=None):
	institution = get_object_or_404(Institution, code=code)
	autonomous_systems = institution.autonomous_systems.all().order_by('as_number')
	ipv4_subnets = institution.ipv4_subnets.all().order_by('network_address', 'subnet_bits')

	return render(request, 'institutions_details.html', {
		'header_active': 'institutions',
		'institution': institution,
		'autonomous_systems': autonomous_systems,
		'ipv4_subnets': ipv4_subnets,
		'can_edit': institution.can_edit(request.user),
	})


@login_required
def list_autonomous_systems(request):
	autonomous_systems = AutonomousSystem.objects.all().order_by('as_number')
	can_create = Institution.objects.filter(owners=request.user.id).exists()

	return render(request, 'autonomous_systems_list.html', {
		'header_active': 'autonomous_systems',
		'autonomous_systems': autonomous_systems,
		'can_create': can_create,
	})


@login_required
def edit_autonomous_system(request, as_number=None):
	if as_number:
		mode = 'edit'
		autonomous_system = get_object_or_404(AutonomousSystem, as_number=as_number)
		if not autonomous_system.can_edit(request.user):
			raise PermissionDenied
	else:
		mode = 'create'
		autonomous_system = AutonomousSystem()
		institution_code = request.GET.get('institution', None)
		if institution_code:
			autonomous_system.institution = Institution.objects.get(code=institution_code)

	# model.is_valid() modifies model. :(
	original = {
		'as_number': autonomous_system.as_number,
	}

	if request.method == 'POST':
		form = AutonomousSystemForm(instance=autonomous_system, data=request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('lana_data:autonomous_system-details', kwargs={'as_number': autonomous_system.as_number}))
	else:
		form = AutonomousSystemForm(instance=autonomous_system)

	form.fields['institution'].queryset = Institution.objects.filter(owners=request.user.id).order_by('code')

	form.helper = FormHelper()
	form.helper.form_class = 'form-horizontal'
	form.helper.label_class = 'col-md-2'
	form.helper.field_class = 'col-md-4'
	form.helper.html5_required = True
	if mode == 'create':
		form.helper.add_input(Submit("submit", "Create"))
	else:
		form.helper.add_input(Submit("submit", "Save"))

	return render(request, 'autonomous_systems_edit.html', {
		'header_active': 'autonomous_systems',
		'mode': mode,
		'original': original,
		'form': form,
	})


@login_required
def show_autonomous_system(request, as_number=None):
	autonomous_system = get_object_or_404(AutonomousSystem, as_number=as_number)

	return render(request, 'autonomous_systems_details.html', {
		'header_active': 'autonomous_systems',
		'autonomous_system': autonomous_system,
		'can_edit': autonomous_system.can_edit(request.user),
	})


@login_required
def list_ipv4(request):
	subnets = IPv4Subnet.objects.all().order_by('network_address', 'subnet_bits')
	can_create = Institution.objects.filter(owners=request.user.id).exists()

	return render(request, 'ipv4_list.html', {
		'header_active': 'ipv4',
		'subnets': subnets,
		'can_create': can_create,
	})


@login_required
def edit_ipv4(request, network_address=None, subnet_bits=None):
	if network_address and subnet_bits:
		mode = 'edit'
		subnet = get_object_or_404(IPv4Subnet, network_address=network_address, subnet_bits=subnet_bits)
		if not subnet.can_edit(request.user):
			raise PermissionDenied
	else:
		mode = 'create'
		subnet = IPv4Subnet()
		institution_code = request.GET.get('institution', None)
		if institution_code:
			subnet.institution = Institution.objects.get(code=institution_code)

	# model.is_valid() modifies model. :(
	original = {
		'network_address': subnet.network_address,
		'subnet_bits': subnet.subnet_bits,
	}

	if request.method == 'POST':
		form = IPv4SubnetForm(instance=subnet, data=request.POST)
		if form.is_valid():
			subnet = form.save()
			return HttpResponseRedirect(reverse('lana_data:ipv4-details', kwargs={'network_address': subnet.network_address, 'subnet_bits': subnet.subnet_bits}))
	else:
		form = IPv4SubnetForm(instance=subnet)

	form.fields['institution'].queryset = Institution.objects.filter(owners=request.user.id).order_by('code')

	form.helper = FormHelper()
	form.helper.form_class = 'form-horizontal'
	form.helper.label_class = 'col-md-2'
	form.helper.field_class = 'col-md-4'
	form.helper.html5_required = True
	if mode == 'create':
		form.helper.add_input(Submit("submit", "Create"))
	else:
		form.helper.add_input(Submit("submit", "Save"))

	return render(request, 'ipv4_edit.html', {
		'header_active': 'ipv4',
		'mode': mode,
		'original': original,
		'form': form,
	})


@login_required
def show_ipv4(request, network_address=None, subnet_bits=None):
	subnet = get_object_or_404(IPv4Subnet, network_address=network_address, subnet_bits=subnet_bits)

	return render(request, 'ipv4_details.html', {
		'header_active': 'ipv4',
		'subnet': subnet,
		'can_edit': subnet.can_edit(request.user),
	})
