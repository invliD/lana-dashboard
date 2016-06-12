from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.vary import vary_on_headers

from lana_dashboard.lana_data.forms import AutonomousSystemForm
from lana_dashboard.lana_data.models import AutonomousSystem, Host, Institution, Tunnel
from lana_dashboard.lana_data.utils import (
	geojson_from_autonomous_systems,
	get_object_for_edit_or_40x,
	get_object_for_view_or_404,
	list_objects_for_view,
)


@login_required
@vary_on_headers('Accept')
def list_autonomous_systems(request):
	accept = request.META.get('HTTP_ACCEPT')
	if accept == 'application/vnd.geo+json':
		return list_autonomous_systems_geojson(request)
	else:
		return list_autonomous_systems_web(request)


def list_autonomous_systems_geojson(request):
	autonomous_systems = list_objects_for_view(AutonomousSystem, request).select_related('institution')
	return JsonResponse(geojson_from_autonomous_systems(autonomous_systems))


def list_autonomous_systems_web(request):
	autonomous_systems = list_objects_for_view(AutonomousSystem, request).select_related('institution')
	can_create = Institution.objects.filter(owners=request.user.id).exists()

	return render(request, 'autonomous_systems_list.html', {
		'header_active': 'autonomous_systems',
		'autonomous_systems': autonomous_systems,
		'can_create': can_create,
	})


@login_required
@require_POST
def delete_autonomous_system(request, as_number):
	autonomous_system = get_object_for_edit_or_40x(AutonomousSystem, request, as_number=as_number)

	hosts = Host.objects.filter(autonomous_system=autonomous_system)
	if hosts.exists():
		messages.error(request, 'You cannot delete this Autonomous System. There are still Hosts associated with it.')
		return HttpResponseRedirect(reverse('lana_data:autonomous_system-details', kwargs={'as_number': autonomous_system.as_number}))

	autonomous_system.delete()
	return HttpResponseRedirect(reverse('lana_data:autonomous_systems'))


@login_required
def edit_autonomous_system(request, as_number=None):
	if as_number:
		mode = 'edit'
		autonomous_system = get_object_for_edit_or_40x(AutonomousSystem, request, select_related=['institution'], as_number=as_number)
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

	form.fields['institution'].queryset = Institution.objects.filter(owners=request.user.id)

	form.helper = FormHelper()
	form.helper.form_class = 'form-horizontal'
	form.helper.label_class = 'col-xs-4 col-md-3 col-lg-2'
	form.helper.field_class = 'col-xs-8 col-md-6 col-lg-5 col-xl-4'
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
@vary_on_headers('Accept')
def show_autonomous_system(request, as_number=None):
	accept = request.META.get('HTTP_ACCEPT')
	if accept == 'application/vnd.geo+json':
		return show_autonomous_system_geojson(request, as_number=as_number)
	else:
		return show_autonomous_system_web(request, as_number=as_number)


def show_autonomous_system_geojson(request, as_number=None):
	autonomous_system = get_object_for_view_or_404(AutonomousSystem, request, select_related=['institution'], as_number=as_number)
	return JsonResponse(geojson_from_autonomous_systems([autonomous_system]))


def show_autonomous_system_web(request, as_number=None):
	autonomous_system = get_object_for_view_or_404(AutonomousSystem, request, select_related=['institution'], as_number=as_number)
	hosts = list_objects_for_view(Host, request, autonomous_system=autonomous_system)
	tunnels = list_objects_for_view(Tunnel, request, Q(endpoint1__host__autonomous_system__as_number=as_number) | Q(endpoint2__host__autonomous_system__as_number=as_number)).select_related(
		'endpoint1__host__autonomous_system',
		'endpoint2__host__autonomous_system',
	)

	for tunnel in tunnels:
		if tunnel.endpoint1.autonomous_system.as_number == int(as_number):
			tunnel.peer_endpoint = tunnel.endpoint2
		else:
			tunnel.peer_endpoint = tunnel.endpoint1

	return render(request, 'autonomous_systems_details.html', {
		'header_active': 'autonomous_systems',
		'autonomous_system': autonomous_system,
		'hosts': hosts,
		'tunnels': tunnels,
		'can_edit': autonomous_system.can_edit(request.user),
	})
