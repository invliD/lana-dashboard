from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.vary import vary_on_headers

from lana_dashboard.lana_data.forms import InstitutionForm
from lana_dashboard.lana_data.models import AutonomousSystem, Institution, Tunnel
from lana_dashboard.lana_data.utils import geojson_from_autonomous_systems, geojson_from_tunnels


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
	institution = get_object_or_404(Institution, code=code)
	autonomous_systems = institution.autonomous_systems.all()
	ipv4_subnets = institution.ipv4_subnets.all()
	show_map = institution.autonomous_systems.all().exclude(location_lat__isnull=True).exclude(location_lng__isnull=True).exists()

	return render(request, 'institutions_details.html', {
		'header_active': 'institutions',
		'institution': institution,
		'autonomous_systems': autonomous_systems,
		'ipv4_subnets': ipv4_subnets,
		'can_edit': institution.can_edit(request.user),
		'show_map': show_map,
	})


@login_required
@vary_on_headers('Content-Type')
def list_institution_autonomous_systems(request, code=None):
	accept = request.META.get('HTTP_ACCEPT')
	if accept == 'application/vnd.geo+json':
		return list_institution_autonomous_systems_geojson(request, code=code)
	else:
		raise Http404


def list_institution_autonomous_systems_geojson(request, code=None):
	get_object_or_404(Institution, code=code)
	autonomous_systems = AutonomousSystem.objects.all().filter(institution__code=code)
	return JsonResponse(geojson_from_autonomous_systems(autonomous_systems))


@login_required
@vary_on_headers('Content-Type')
def list_institution_tunnels(request, code=None):
	accept = request.META.get('HTTP_ACCEPT')
	if accept == 'application/vnd.geo+json':
		return list_institution_tunnels_geojson(request, code=code)
	else:
		raise Http404


def list_institution_tunnels_geojson(request, code=None):
	get_object_or_404(Institution, code=code)
	autonomous_systems = AutonomousSystem.objects.all().filter(institution__code=code)
	as_ids = [autonomous_system.id for autonomous_system in autonomous_systems]
	tunnels = Tunnel.objects.all().filter(endpoint1__autonomous_system__id__in=as_ids).filter(endpoint2__autonomous_system__id__in=as_ids)
	return JsonResponse(geojson_from_tunnels(tunnels))
