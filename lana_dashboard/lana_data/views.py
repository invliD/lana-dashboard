from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from lana_dashboard.lana_data.forms import AutonomousSystemForm, InstitutionForm, IPv4SubnetForm, TunnelForm, TunnelEndpointForm

from lana_dashboard.lana_data.models import AutonomousSystem, Institution, IPv4Subnet, Tunnel, TunnelEndpoint
from lana_dashboard.lana_data.utils import geojson_from_autonomous_systems


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
	accept = request.META.get('HTTP_ACCEPT')
	if accept == 'application/vnd.geo+json':
		return show_autonomous_system_geojson(request, as_number=as_number)
	else:
		return show_autonomous_system_web(request, as_number=as_number)


def show_autonomous_system_geojson(request, as_number=None):
	autonomous_system = get_object_or_404(AutonomousSystem, as_number=as_number)
	return JsonResponse(geojson_from_autonomous_systems([autonomous_system]))


def show_autonomous_system_web(request, as_number=None):
	autonomous_system = get_object_or_404(AutonomousSystem, as_number=as_number)
	tunnels = Tunnel.objects.all().filter(Q(endpoint1__autonomous_system__as_number=as_number) | Q(endpoint2__autonomous_system__as_number=as_number))

	for tunnel in tunnels:
		if tunnel.endpoint1.autonomous_system.as_number == int(as_number):
			tunnel.peer_endpoint = tunnel.endpoint2
		else:
			tunnel.peer_endpoint = tunnel.endpoint1

	return render(request, 'autonomous_systems_details.html', {
		'header_active': 'autonomous_systems',
		'autonomous_system': autonomous_system,
		'tunnels': tunnels,
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


@login_required
def list_tunnels(request):
	tunnels = Tunnel.objects.all().order_by('endpoint1__autonomous_system__as_number', 'endpoint2__autonomous_system__as_number')
	can_create = AutonomousSystem.objects.filter(institution__owners=request.user.id).exists()

	return render(request, 'tunnels_list.html', {
		'header_active': 'tunnels',
		'tunnels': tunnels,
		'can_create': can_create,
	})


@login_required
def edit_tunnel(request, as_number1=None, as_number2=None):
	if as_number1 and as_number2:
		mode = 'edit'
		tunnel = get_object_or_404(Tunnel, endpoint1__autonomous_system__as_number=as_number1, endpoint2__autonomous_system__as_number=as_number2)
		if not tunnel.can_edit(request.user):
			raise PermissionDenied
		original = {
			'as_number1': tunnel.endpoint1.autonomous_system.as_number,
			'as_number2': tunnel.endpoint2.autonomous_system.as_number,
		}
	else:
		mode = 'create'
		tunnel = Tunnel()
		tunnel.endpoint1 = TunnelEndpoint()
		tunnel.endpoint2 = TunnelEndpoint()
		original = {}

	if request.method == 'POST':
		tunnel_form = TunnelForm(instance=tunnel, data=request.POST, prefix='tunnel')
		endpoint1_form = TunnelEndpointForm(instance=tunnel.endpoint1, data=request.POST, prefix='endpoint1')
		endpoint2_form = TunnelEndpointForm(instance=tunnel.endpoint2, data=request.POST, prefix='endpoint2')

		if tunnel_form.is_valid() and endpoint1_form.is_valid() and endpoint2_form.is_valid():
			endpoint1 = endpoint1_form.save(commit=False)
			endpoint2 = endpoint2_form.save(commit=False)

			lower_as_number = min(endpoint1.autonomous_system.as_number, endpoint2.autonomous_system.as_number)
			higher_as_number = max(endpoint1.autonomous_system.as_number, endpoint2.autonomous_system.as_number)

			error_message = None
			if not tunnel.can_edit(request.user):
				error_message = "You cannot create a tunnel between two Autonomous Systems you don't manage."
			elif endpoint1.autonomous_system.as_number == endpoint2.autonomous_system.as_number:
				error_message = "You cannot create a tunnel within one Autonomous System."
			elif Tunnel.objects.all().filter(endpoint1__autonomous_system__as_number=lower_as_number, endpoint2__autonomous_system__as_number=higher_as_number).filter(~Q(id=tunnel.id)).exists():
				error_message = "A tunnel between these two Autonomous Systems already exists."

			if error_message:
				endpoint1_form.add_error('autonomous_system', error_message)
				endpoint2_form.add_error('autonomous_system', error_message)
			else:
				endpoint1.save()
				endpoint2.save()
				tunnel = tunnel_form.save(commit=False)
				tunnel.endpoint1 = endpoint1
				tunnel.endpoint2 = endpoint2
				if endpoint1.autonomous_system.as_number > endpoint2.autonomous_system.as_number:
					tunnel.endpoint1, tunnel.endpoint2 = tunnel.endpoint2, tunnel.endpoint1
				tunnel.save()
				return HttpResponseRedirect(reverse('lana_data:tunnels'))
	else:
		tunnel_form = TunnelForm(instance=tunnel, prefix='tunnel')
		endpoint1_form = TunnelEndpointForm(instance=tunnel.endpoint1, prefix='endpoint1')
		endpoint2_form = TunnelEndpointForm(instance=tunnel.endpoint2, prefix='endpoint2')

	tunnel_form.helper = FormHelper()
	tunnel_form.helper.form_tag = False
	tunnel_form.helper.label_class = 'col-md-2'
	tunnel_form.helper.field_class = 'col-md-4'
	tunnel_form.helper.html5_required = True

	helper = FormHelper()
	helper.form_tag = False
	helper.disable_csrf = True
	helper.label_class = 'col-md-4'
	helper.field_class = 'col-md-8'
	helper.html5_required = True

	endpoint1_form.helper = helper
	endpoint2_form.helper = helper

	return render(request, 'tunnels_edit.html', {
		'header_active': 'tunnels',
		'mode': mode,
		'original': original,
		'tunnel_form': tunnel_form,
		'endpoint1_form': endpoint1_form,
		'endpoint2_form': endpoint2_form,
	})


@login_required
def show_tunnel(request, as_number1=None, as_number2=None):
	tunnel = get_object_or_404(Tunnel, endpoint1__autonomous_system__as_number=as_number1, endpoint2__autonomous_system__as_number=as_number2)

	return render(request, 'tunnels_details.html', {
		'header_active': 'tunnels',
		'tunnel': tunnel,
		'endpoints': [tunnel.endpoint1, tunnel.endpoint2],
		'can_edit': tunnel.can_edit(request.user),
	})
