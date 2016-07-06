from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from lana_dashboard.lana_data.forms import HostForm
from lana_dashboard.lana_data.models import AutonomousSystem, Host, TunnelEndpoint
from lana_dashboard.lana_data.utils import get_object_for_edit_or_40x, get_object_for_view_or_404


@login_required
@require_POST
def delete_host(request, fqdn):
	host = get_object_for_edit_or_40x(Host, request, fqdn=fqdn)

	tunnel_endpoints = TunnelEndpoint.objects.filter(host=host)
	if tunnel_endpoints.exists():
		messages.error(request, 'You cannot delete this Host. There are still Tunnels associated with it.')
		return HttpResponseRedirect(reverse('lana_data:host-details', kwargs={'fqdn': host.fqdn}))

	host.delete()
	return HttpResponseRedirect(reverse('lana_data:autonomous_system-details', kwargs={'as_number': host.autonomous_system.as_number}))


@login_required
def edit_host(request, fqdn=None, as_number=None):
	if fqdn:
		mode = 'edit'
		host = get_object_for_edit_or_40x(Host, request, select_related=['autonomous_system', 'autonomous_system__institution'], fqdn=fqdn)
	else:
		mode = 'create'
		host = Host()
		if as_number:
			host.autonomous_system = AutonomousSystem.objects.get(as_number=as_number)

	# model.is_valid() modifies model. :(
	original = {
		'fqdn': host.fqdn,
		'as_number': host.autonomous_system.as_number,
	}

	if request.method == 'POST':
		form = HostForm(instance=host, data=request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('lana_data:host-details', kwargs={'fqdn': host.fqdn}))
	else:
		form = HostForm(instance=host)

	form.fields['autonomous_system'].queryset = AutonomousSystem.objects.filter(institution__owners=request.user.id)

	form.helper = FormHelper()
	form.helper.form_class = 'form-horizontal'
	form.helper.label_class = 'col-xs-4 col-md-3 col-lg-2'
	form.helper.field_class = 'col-xs-8 col-md-6 col-lg-5 col-xl-4'
	form.helper.html5_required = True
	if mode == 'create':
		form.helper.add_input(Submit("submit", "Create"))
	else:
		form.helper.add_input(Submit("submit", "Save"))

	return render(request, 'hosts_edit.html', {
		'header_active': 'autonomous_systems',
		'mode': mode,
		'original': original,
		'form': form,
	})


@login_required
def show_host(request, fqdn):
	host = get_object_for_view_or_404(Host, request, select_related=[
		'autonomous_system',
		'autonomous_system__institution',
	], fqdn=fqdn)

	return render(request, 'hosts_details.html', {
		'header_active': 'autonomous_systems',
		'host': host,
		'can_edit': host.autonomous_system.can_edit(request.user),
	})
