from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from lana_dashboard.lana_data.forms import IPv4SubnetForm
from lana_dashboard.lana_data.models import Institution, IPv4Subnet
from lana_dashboard.lana_data.utils import (
	get_object_for_edit_or_40x,
	get_object_for_view_or_404,
	list_objects_for_view,
)


@login_required
def list_ipv4(request):
	subnets = list_objects_for_view(IPv4Subnet, request)
	can_create = Institution.objects.filter(owners=request.user.id).exists()

	return render(request, 'ipv4_list.html', {
		'header_active': 'ipv4',
		'ipv4_subnets': subnets,
		'can_create': can_create,
	})


@login_required
def delete_ipv4(request, network):
	if request.method != 'POST':
		raise PermissionDenied
	subnet = get_object_for_edit_or_40x(IPv4Subnet, request, network=network)

	subnet.delete()
	return HttpResponseRedirect(reverse('lana_data:ipv4'))


@login_required
def edit_ipv4(request, network=None):
	if network:
		mode = 'edit'
		subnet = get_object_for_edit_or_40x(IPv4Subnet, request, network=network)
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
	subnet = get_object_for_view_or_404(IPv4Subnet, request, network=network)

	return render(request, 'ipv4_details.html', {
		'header_active': 'ipv4',
		'subnet': subnet,
		'can_edit': subnet.can_edit(request.user),
	})
