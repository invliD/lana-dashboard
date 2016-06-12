from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.vary import vary_on_headers

from lana_dashboard.lana_data.forms import InstitutionForm
from lana_dashboard.lana_data.models import AutonomousSystem, Institution, IPv4Subnet, Tunnel
from lana_dashboard.lana_data.utils import (
	geojson_from_autonomous_systems,
	geojson_from_tunnels,
	get_object_for_edit_or_40x,
	get_object_for_view_or_404,
	list_objects_for_view,
)


@login_required
def list_institutions(request):
	institutions = list_objects_for_view(Institution, request).prefetch_related('owners')

	return render(request, 'institutions_list.html', {
		'header_active': 'institutions',
		'institutions': institutions,
	})


@login_required
@require_POST
def delete_institution(request, code):
	institution = get_object_for_edit_or_40x(Institution, request, code=code)

	error = False
	autonomous_systems = AutonomousSystem.objects.filter(institution=institution)
	if autonomous_systems.exists():
		messages.error(request, 'You cannot delete this Institution. There are still Autonomous Systems associated with it.')
		error = True
	ipv4_subnets = IPv4Subnet.objects.filter(institution=institution)
	if ipv4_subnets.exists():
		messages.error(request, 'You cannot delete this Institution. There are still IPv4 Subnets associated with it.')
		error = True
	if error:
		return HttpResponseRedirect(reverse('lana_data:institution-details', kwargs={'code': institution.code}))

	institution.delete()
	return HttpResponseRedirect(reverse('lana_data:institutions'))


@login_required
def edit_institution(request, code=None):
	if code:
		mode = 'edit'
		institution = get_object_for_edit_or_40x(Institution, request, code=code)
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
	form.helper.label_class = 'col-xs-4 col-md-3 col-lg-2'
	form.helper.field_class = 'col-xs-8 col-md-6 col-lg-5 col-xl-4'
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
	institution = get_object_for_view_or_404(Institution, request, code=code)
	autonomous_systems = list_objects_for_view(AutonomousSystem, request, institution=institution)
	ipv4_subnets = list_objects_for_view(IPv4Subnet, request, institution=institution)
	tunnels = list_objects_for_view(Tunnel, request, Q(endpoint1__host__autonomous_system__institution=institution) | Q(endpoint2__host__autonomous_system__institution=institution)).select_related(
		'endpoint1__host__autonomous_system',
		'endpoint2__host__autonomous_system',
		'endpoint1__host__autonomous_system__institution',
		'endpoint2__host__autonomous_system__institution',
	)
	show_map = list_objects_for_view(AutonomousSystem, request, institution=institution).exclude(location_lat__isnull=True).exclude(location_lng__isnull=True).exists()

	for tunnel in tunnels:
		for i, endpoint in enumerate([tunnel.endpoint1, tunnel.endpoint2]):
			endpoint.autonomous_system.show_link = endpoint.autonomous_system.can_view(request.user)

	return render(request, 'institutions_details.html', {
		'header_active': 'institutions',
		'institution': institution,
		'autonomous_systems': autonomous_systems,
		'ipv4_subnets': ipv4_subnets,
		'tunnels': tunnels,
		'can_edit': institution.can_edit(request.user),
		'show_map': show_map,
	})


@login_required
@vary_on_headers('Accept')
def list_institution_autonomous_systems(request, code=None):
	accept = request.META.get('HTTP_ACCEPT')
	if accept == 'application/vnd.geo+json':
		return list_institution_autonomous_systems_geojson(request, code=code)
	else:
		raise Http404


def list_institution_autonomous_systems_geojson(request, code=None):
	institution = get_object_for_view_or_404(Institution, request, code=code)
	autonomous_systems = list_objects_for_view(AutonomousSystem, request, institution=institution).select_related('institution')
	return JsonResponse(geojson_from_autonomous_systems(autonomous_systems))


@login_required
@vary_on_headers('Accept')
def list_institution_tunnels(request, code=None):
	accept = request.META.get('HTTP_ACCEPT')
	if accept == 'application/vnd.geo+json':
		return list_institution_tunnels_geojson(request, code=code)
	else:
		raise Http404


def list_institution_tunnels_geojson(request, code=None):
	institution = get_object_for_view_or_404(Institution, request, code=code)
	tunnels = list_objects_for_view(Tunnel, request, endpoint1__host__autonomous_system__institution=institution).filter(endpoint2__host__autonomous_system__institution=institution).select_related(
		'endpoint1__host__autonomous_system',
		'endpoint2__host__autonomous_system',
	)
	return JsonResponse(geojson_from_tunnels(tunnels))
