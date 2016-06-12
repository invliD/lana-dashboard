from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.http import Http404
from django.shortcuts import render
from django.template.loader import render_to_string

from lana_dashboard.lana_data.models import FastdTunnel, Tunnel
from lana_dashboard.lana_data.utils import get_object_for_view_or_404
from lana_dashboard.lana_generator.forms import FastdGeneratorForm


def generate_fastd(request, as_number1, as_number2, endpoint_number):
	tunnel = get_object_for_view_or_404(Tunnel, request, with_subclasses=True, endpoint1__host__autonomous_system__as_number=as_number1, endpoint2__host__autonomous_system__as_number=as_number2)
	if not isinstance(tunnel, FastdTunnel) or not tunnel.is_config_complete():
		raise Http404
	config = None

	if request.method == "POST":
		form = FastdGeneratorForm(data=request.POST)
		if form.is_valid():
			local_endpoint = tunnel.real_endpoint1
			remote_endpoint = tunnel.real_endpoint2
			if int(endpoint_number) == 2:
				local_endpoint, remote_endpoint = remote_endpoint, local_endpoint
			config = render_to_string('fastd.conf', {
				'tunnel': tunnel,
				'tunnel_name': form.cleaned_data['tunnel_name'],
				'local_endpoint': local_endpoint,
				'remote_endpoint': remote_endpoint,
				'remote_host': remote_endpoint.host.external_hostname or remote_endpoint.host.external_ipv4.ip,
			})
	else:
		form = FastdGeneratorForm()

	form.helper = FormHelper()
	form.helper.form_class = 'form-horizontal'
	form.helper.label_class = 'col-xs-4 col-md-3 col-lg-2'
	form.helper.field_class = 'col-xs-8 col-md-6 col-lg-5 col-xl-4'
	form.helper.html5_required = True
	form.helper.add_input(Submit("submit", "Generate"))

	return render(request, 'generate_fastd.html', {
		'tunnel': tunnel,
		'form': form,
		'config': config,
	})
