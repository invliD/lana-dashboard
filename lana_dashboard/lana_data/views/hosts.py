from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from lana_dashboard.lana_data.models import Host
from lana_dashboard.lana_data.utils import get_object_for_view_or_404


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
