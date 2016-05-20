from crispy_forms.helper import FormHelper
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.vary import vary_on_headers

from lana_dashboard.lana_data.forms import TunnelEndpointForm, TunnelForm
from lana_dashboard.lana_data.models import AutonomousSystem, Tunnel, TunnelEndpoint
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
				if tunnel.protocol == tunnel.PROTOCOL_FASTD:
					as1 = endpoint1.autonomous_system.as_number
					as2 = endpoint2.autonomous_system.as_number
					if not endpoint1.port and as2 <= 65535:
						endpoint1.port = as2
					if not endpoint2.port and as1 <= 65535:
						endpoint2.port = as1

				endpoint1.save()
				endpoint2.save()
				tunnel = tunnel_form.save(commit=False)
				tunnel.endpoint1 = endpoint1
				tunnel.endpoint2 = endpoint2
				if endpoint1.autonomous_system.as_number > endpoint2.autonomous_system.as_number:
					tunnel.endpoint1, tunnel.endpoint2 = tunnel.endpoint2, tunnel.endpoint1
				tunnel.save()
				return HttpResponseRedirect(reverse('lana_data:tunnel-details', kwargs={
					'as_number1': tunnel.endpoint1.autonomous_system.as_number,
					'as_number2': endpoint2.autonomous_system.as_number
				}))
	else:
		tunnel_form = TunnelForm(instance=tunnel, prefix='tunnel')
		endpoint1_form = TunnelEndpointForm(instance=tunnel.endpoint1, prefix='endpoint1')
		endpoint2_form = TunnelEndpointForm(instance=tunnel.endpoint2, prefix='endpoint2')

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
		tunnel.endpoint1.config_generation_url = tunnel.get_config_generation_url(1)
		tunnel.endpoint2.config_generation_url = tunnel.get_config_generation_url(2)

	return render(request, 'tunnels_details.html', {
		'header_active': 'tunnels',
		'tunnel': tunnel,
		'endpoints': [tunnel.endpoint1, tunnel.endpoint2],
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
