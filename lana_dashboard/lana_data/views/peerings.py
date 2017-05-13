import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from lana_dashboard.lana_data.forms import PeeringForm
from lana_dashboard.lana_data.models import Peering, Tunnel, TunnelPeering
from lana_dashboard.lana_data.utils import get_object_for_edit_or_40x, get_object_for_view_or_404


@login_required
@require_POST
def delete_peering(request, as_number1=None, as_number2=None):
	peering = get_object_for_edit_or_40x(Peering, request, with_subclasses=True, tunnelpeering__tunnel__endpoint1__host__autonomous_system__as_number=as_number1, tunnelpeering__tunnel__endpoint2__host__autonomous_system__as_number=as_number2)
	# HACK: Assume it's a TunnelPeering.
	tunnel = peering.tunnel
	peering.delete()
	return HttpResponseRedirect(reverse('lana_data:tunnel-details', kwargs={'as_number1': tunnel.endpoint1.autonomous_system.as_number, 'as_number2': tunnel.endpoint2.autonomous_system.as_number}))


@login_required
def edit_peering(request, as_number1=None, as_number2=None):
	if as_number1 and as_number2:
		mode = 'edit'
		peering = get_object_for_edit_or_40x(Peering, request, with_subclasses=True, tunnelpeering__tunnel__endpoint1__host__autonomous_system__as_number=as_number1, tunnelpeering__tunnel__endpoint2__host__autonomous_system__as_number=as_number2)
		original = {
			'as_number1': peering.host1.autonomous_system.as_number,
			'as_number2': peering.host2.autonomous_system.as_number,
		}
	else:
		mode = 'create'
		tunnel_name = request.GET.get('tunnel', None)
		if tunnel_name:
			peering = TunnelPeering()
			match = re.match(r'^AS(\d+)-AS(\d+)$', tunnel_name)
			as_number1 = match.group(1)
			as_number2 = match.group(2)
			tunnel = get_object_for_edit_or_40x(Tunnel, request, endpoint1__host__autonomous_system__as_number=as_number1, endpoint2__host__autonomous_system__as_number=as_number2)
			if hasattr(tunnel, "peering"):
				raise SuspiciousOperation("There can only be one TunnelPeering per Tunnel")
			peering.tunnel = tunnel
		else:
			raise Http404
		original = {}

	if request.method == 'POST':
		form = PeeringForm(instance=peering, data=request.POST)
		if form.is_valid():
			peering = form.save()
			return HttpResponseRedirect(reverse('lana_data:peering-details', kwargs={'as_number1': peering.host1.autonomous_system.as_number, 'as_number2': peering.host2.autonomous_system.as_number}))
	else:
		form = PeeringForm(instance=peering)

	form.helper = FormHelper()
	form.helper.form_class = 'form-horizontal'
	form.helper.label_class = 'col-xs-4 col-md-3 col-lg-2'
	form.helper.field_class = 'col-xs-8 col-md-6 col-lg-5 col-xl-4'
	form.helper.html5_required = True
	if mode == 'create':
		form.helper.add_input(Submit("submit", "Create"))
	else:
		form.helper.add_input(Submit("submit", "Save"))

	return render(request, 'peerings_edit.html', {
		'header_active': 'tunnels',
		'mode': mode,
		'original': original,
		'form': form,
	})


@login_required
def show_peering(request, as_number1=None, as_number2=None):
	# FIXME: with_subclasses breaks select_related.
	peering = get_object_for_view_or_404(Peering, request, with_subclasses=True, tunnelpeering__tunnel__endpoint1__host__autonomous_system__as_number=as_number1, tunnelpeering__tunnel__endpoint2__host__autonomous_system__as_number=as_number2)

	for i, host in enumerate([peering.host1, peering.host2]):
		host.autonomous_system.show_link = host.autonomous_system.can_view(request.user)

	return render(request, 'peerings_details.html', {
		'header_active': 'tunnels',
		'peering': peering,
		'hosts': [peering.host1, peering.host2],
		'can_edit': peering.can_edit(request.user),
	})
