from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from lana_dashboard.lana_data.forms import IPv4SubnetForm
from lana_dashboard.lana_data.models import Host, Institution, IPv4Subnet
from lana_dashboard.lana_data.utils import (
	get_object_for_edit_or_40x,
	get_object_for_view_or_404,
	list_objects_for_view,
)


@login_required
def list_ipv4(request):
	subnets = list_objects_for_view(IPv4Subnet, request).select_related('institution')
	can_create = Institution.objects.filter(owners=request.user.id).exists()

	return render(request, 'ipv4_list.html', {
		'header_active': 'ipv4',
		'ipv4_subnets': subnets,
		'can_create': can_create,
	})


@login_required
@require_POST
def delete_ipv4(request, network):
	subnet = get_object_for_edit_or_40x(IPv4Subnet, request, network=network)

	subnet.delete()
	return HttpResponseRedirect(reverse('lana_data:ipv4'))


@login_required
def edit_ipv4(request, network=None):
	if network:
		mode = 'edit'
		try:
			subnet = get_object_for_edit_or_40x(IPv4Subnet, request, select_related=['institution'], network=network)
		except ValidationError:
			raise Http404
	else:
		mode = 'create'
		subnet = IPv4Subnet()
		institution_code = request.GET.get('institution', None)
		if institution_code:
			subnet.institution = Institution.objects.get(code=institution_code)

	# model.is_valid() modifies model. :(
	original = {
		'network': str(subnet.network),
	}

	if request.method == 'POST':
		form = IPv4SubnetForm(instance=subnet, data=request.POST)
		if form.is_valid():
			subnet = form.save()
			return HttpResponseRedirect(reverse('lana_data:ipv4-details', kwargs={'network': subnet.network}))
	else:
		form = IPv4SubnetForm(instance=subnet)

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

	return render(request, 'ipv4_edit.html', {
		'header_active': 'ipv4',
		'mode': mode,
		'original': original,
		'form': form,
	})


@login_required
def show_ipv4(request, network):
	try:
		subnet = get_object_for_view_or_404(IPv4Subnet, request, select_related=['institution'], network=network)
	except ValidationError:
		raise Http404

	hosts = list_objects_for_view(Host, request, Q(internal_ipv4__net_contained_or_equal=subnet.network) | Q(tunnel_ipv4__net_contained_or_equal=subnet.network))

	return render(request, 'ipv4_details.html', {
		'header_active': 'ipv4',
		'subnet': subnet,
		'hosts': hosts,
		'can_edit': subnet.can_edit(request.user),
	})
