from crispy_forms.helper import FormHelper
from crispy_forms.utils import render_crispy_form
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.context_processors import csrf
from django.views.decorators.vary import vary_on_headers

from lana_dashboard.lana_data.forms import (
	FastdTunnelEndpointForm,
	FastdTunnelForm,
	TunnelEndpointForm,
	TunnelForm,
	TunnelProtocolForm,
)

from lana_dashboard.lana_data.models import AutonomousSystem, Tunnel
from lana_dashboard.lana_data.utils import (
	geojson_from_autonomous_systems,
	geojson_from_tunnels,
	get_object_with_subclasses_or_404,
)


@login_required
@vary_on_headers('Content-Type')
def list_tunnels(request):
	accept = request.META.get('HTTP_ACCEPT')
	if accept == 'application/vnd.geo+json':
		return list_tunnels_geojson(request)
	else:
		return list_tunnels_web(request)


def list_tunnels_geojson(request):
	tunnels = Tunnel.objects.all()
	return JsonResponse(geojson_from_tunnels(tunnels))


def list_tunnels_web(request):
	tunnels = Tunnel.objects.all()
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
		tunnel = get_object_with_subclasses_or_404(Tunnel, endpoint1__autonomous_system__as_number=as_number1, endpoint2__autonomous_system__as_number=as_number2)
		if not tunnel.can_edit(request.user):
			raise PermissionDenied
		endpoint1 = tunnel.real_endpoint1
		endpoint2 = tunnel.real_endpoint2
		protocol = tunnel.protocol
		original = {
			'protocol_name': tunnel.protocol_name,
			'as_number1': tunnel.endpoint1.autonomous_system.as_number,
			'as_number2': tunnel.endpoint2.autonomous_system.as_number,
		}
	else:
		mode = 'create'
		tunnel = None
		endpoint1 = None
		endpoint2 = None
		original = {}

	protocol_form = None
	tunnel_form = None
	endpoint1_form = None
	endpoint2_form = None
	if request.method == 'POST':
		if mode == 'create':
			protocol_form = TunnelProtocolForm(data=request.POST, prefix='protocol')
			if protocol_form.is_valid():
				protocol = protocol_form.cleaned_data['protocol']
			else:
				protocol = None

		if protocol is not None:
			tunnel_form, endpoint1_form, endpoint2_form = create_forms(protocol, tunnel, endpoint1, endpoint2, request.POST)

			if tunnel_form.is_valid() and endpoint1_form.is_valid() and endpoint2_form.is_valid():
				endpoint1 = endpoint1_form.save(commit=False)
				endpoint2 = endpoint2_form.save(commit=False)

				lower_as_number = min(endpoint1.autonomous_system.as_number, endpoint2.autonomous_system.as_number)
				higher_as_number = max(endpoint1.autonomous_system.as_number, endpoint2.autonomous_system.as_number)

				error_message = None
				exists_filter = Q(endpoint1__autonomous_system__as_number=lower_as_number, endpoint2__autonomous_system__as_number=higher_as_number)
				if tunnel is not None:
					exists_filter &= ~Q(id=tunnel.id)
				if not endpoint1.autonomous_system.can_edit(request.user) and not endpoint2.autonomous_system.can_edit(request.user):
					error_message = "You cannot create a tunnel between two Autonomous Systems you don't manage."
				elif endpoint1.autonomous_system.as_number == endpoint2.autonomous_system.as_number:
					error_message = "You cannot create a tunnel within one Autonomous System."
				elif Tunnel.objects.filter(exists_filter).exists():
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
					if tunnel.endpoint1.autonomous_system.as_number > tunnel.endpoint2.autonomous_system.as_number:
						tunnel.endpoint1, tunnel.endpoint2 = tunnel.endpoint2, tunnel.endpoint1
					tunnel.prepare_save()
					tunnel.save()
					return HttpResponseRedirect(reverse('lana_data:tunnel-details', kwargs={
						'as_number1': tunnel.endpoint1.autonomous_system.as_number,
						'as_number2': tunnel.endpoint2.autonomous_system.as_number
					}))
	else:
		if mode == 'create':
			protocol_form = TunnelProtocolForm(prefix='protocol')
		else:
			tunnel_form, endpoint1_form, endpoint2_form = create_forms(tunnel.protocol, tunnel, endpoint1, endpoint2)

	if protocol_form is not None:
		protocol_form.helper = FormHelper()
		protocol_form.helper.form_tag = False
		protocol_form.helper.label_class = 'col-xs-4 col-lg-2'
		protocol_form.helper.field_class = 'col-xs-8 col-lg-5 col-xl-4'
		protocol_form.helper.html5_required = True

	return render(request, 'tunnels_edit.html', {
		'header_active': 'tunnels',
		'mode': mode,
		'protocol_form': protocol_form,
		'original': original,
		'tunnel_form': tunnel_form,
		'endpoint1_form': endpoint1_form,
		'endpoint2_form': endpoint2_form,
	})


@login_required
def generate_tunnel_form(request):
	protocol = request.GET.get('protocol')
	tunnel_form, endpoint1_form, endpoint2_form = create_forms(protocol)

	context = {}
	context.update(csrf(request))
	tunnel_html = render_crispy_form(tunnel_form, context=context)
	endpoint1_html = render_crispy_form(endpoint1_form, context=context)
	endpoint2_html = render_crispy_form(endpoint2_form, context=context)

	return JsonResponse({
		'tunnel_form': tunnel_html,
		'endpoint1_form': endpoint1_html,
		'endpoint2_form': endpoint2_html,
	})


def create_forms(protocol, tunnel=None, endpoint1=None, endpoint2=None, data=None):
	if protocol == 'fastd':
		tunnel_form_type = FastdTunnelForm
		endpoint_form_type = FastdTunnelEndpointForm
	elif protocol == 'other':
		tunnel_form_type = TunnelForm
		endpoint_form_type = TunnelEndpointForm
	else:
		raise Http404

	tunnel_form = tunnel_form_type(instance=tunnel, data=data, prefix='tunnel')
	tunnel_form.helper = FormHelper()
	tunnel_form.helper.form_tag = False
	tunnel_form.helper.label_class = 'col-xs-4 col-lg-2'
	tunnel_form.helper.field_class = 'col-xs-8 col-lg-5 col-xl-4'
	tunnel_form.helper.html5_required = True

	helper = FormHelper()
	helper.form_tag = False
	helper.disable_csrf = True
	helper.label_class = 'col-xs-4'
	helper.field_class = 'col-xs-8'
	helper.html5_required = True

	endpoint1_form = endpoint_form_type(instance=endpoint1, data=data, prefix='endpoint1')
	endpoint2_form = endpoint_form_type(instance=endpoint2, data=data, prefix='endpoint2')
	endpoint1_form.helper = helper
	endpoint2_form.helper = helper

	return tunnel_form, endpoint1_form, endpoint2_form


@login_required
@vary_on_headers('Content-Type')
def show_tunnel(request, as_number1=None, as_number2=None):
	accept = request.META.get('HTTP_ACCEPT')
	if accept == 'application/vnd.geo+json':
		return show_tunnel_geojson(request, as_number1=as_number1, as_number2=as_number2)
	else:
		return show_tunnel_web(request, as_number1=as_number1, as_number2=as_number2)


def show_tunnel_geojson(request, as_number1=None, as_number2=None):
	tunnel = get_object_or_404(Tunnel, endpoint1__autonomous_system__as_number=as_number1, endpoint2__autonomous_system__as_number=as_number2)
	return JsonResponse(geojson_from_tunnels([tunnel]))


def show_tunnel_web(request, as_number1=None, as_number2=None):
	tunnel = get_object_with_subclasses_or_404(Tunnel, endpoint1__autonomous_system__as_number=as_number1, endpoint2__autonomous_system__as_number=as_number2)
	show_map = tunnel.endpoint1.autonomous_system.location_lat is not None and tunnel.endpoint1.autonomous_system.location_lng is not None and tunnel.endpoint2.autonomous_system.location_lat is not None and tunnel.endpoint1.autonomous_system.location_lng is not None

	if tunnel.supports_config_generation() and tunnel.is_config_complete():
		tunnel.real_endpoint1.config_generation_url = tunnel.get_config_generation_url(1)
		tunnel.real_endpoint2.config_generation_url = tunnel.get_config_generation_url(2)

	return render(request, 'tunnels_details.html', {
		'header_active': 'tunnels',
		'tunnel': tunnel,
		'endpoints': [tunnel.real_endpoint1, tunnel.real_endpoint2],
		'can_edit': tunnel.can_edit(request.user),
		'show_map': show_map,
	})


@login_required
@vary_on_headers('Content-Type')
def list_tunnel_autonomous_systems(request, as_number1=None, as_number2=None):
	accept = request.META.get('HTTP_ACCEPT')
	if accept == 'application/vnd.geo+json':
		return list_tunnel_autonomous_systems_geojson(request, as_number1=as_number1, as_number2=as_number2)
	else:
		raise Http404


def list_tunnel_autonomous_systems_geojson(request, as_number1=None, as_number2=None):
	tunnel = get_object_or_404(Tunnel, endpoint1__autonomous_system__as_number=as_number1, endpoint2__autonomous_system__as_number=as_number2)
	return JsonResponse(geojson_from_autonomous_systems([tunnel.endpoint1.autonomous_system, tunnel.endpoint2.autonomous_system]))
