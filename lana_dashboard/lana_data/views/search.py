from functools import reduce
from ipaddress import ip_interface
import operator

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render

from lana_dashboard.lana_data.models import AutonomousSystem, Host, Institution, IPv4Subnet
from lana_dashboard.lana_data.utils import list_objects_for_view


@login_required
def search(request, query=None):
	if query is None:
		query = request.GET.get('q')

	results = {}
	if query is not None and query != "":
		result_urls = []

		# Institutions
		db_query = Q(name__icontains=query) | Q(code__icontains=query)
		results['institutions'] = list_objects_for_view(Institution, request, db_query).prefetch_related('owners')
		if len(results['institutions']) == 1:
			result_urls.append(reverse('lana_data:institution-details', kwargs={'code': results['institutions'][0].code}))

		# Autonomous Systems
		db_query = Q(comment__icontains=query)

		as_number = None
		if query[:2].lower() == 'as':
			part2 = query[2:]
			if part2.isdigit():
				as_number = int(part2)
		elif query.isdigit():
			as_number = int(query)
		if as_number is not None:
			db_query |= Q(as_number=as_number)

		results['autonomous_systems'] = list_objects_for_view(AutonomousSystem, request, db_query).select_related('institution')
		if len(results['autonomous_systems']) == 1:
			result_urls.append(reverse('lana_data:autonomous_system-details', kwargs={'as_number': results['autonomous_systems'][0].as_number}))

		# Hosts
		db_query = Q(fqdn__icontains=query) | Q(internal_ipv4__contains=query) | Q(tunnel_ipv4__contains=query) | Q(comment__icontains=query)
		try:
			interface = ip_interface(query)
			db_query |= Q(internal_ipv4__net_contained_or_equal=interface) | Q(tunnel_ipv4__net_contained_or_equal=interface)
		except ValueError:
			pass
		results['hosts'] = list_objects_for_view(Host, request, db_query).select_related(
			'autonomous_system',
			'autonomous_system__institution',
		)
		if len(results['hosts']) == 1:
			result_urls.append(reverse('lana_data:host-details', kwargs={'fqdn': results['hosts'][0].fqdn}))
		else:
			for host in results['hosts']:
				host.autonomous_system.show_link = host.autonomous_system.can_view(request.user)

		# IP addresses / subnets
		db_query = Q(network__contains=query) | Q(comment__icontains=query)
		try:
			interface = ip_interface(query)
			db_query |= Q(network__net_contains_or_equals=interface.network)
		except ValueError:
			pass
		results['ipv4_subnets'] = list_objects_for_view(IPv4Subnet, request, db_query).select_related('institution')
		if len(results['ipv4_subnets']) == 1:
			result_urls.append(reverse('lana_data:ipv4-details', kwargs={'network': results['ipv4_subnets'][0].network}))

		if len(result_urls) == 1 and len(reduce(operator.add, [list(r) for r in results.values()])) == 1:
			return HttpResponseRedirect(result_urls[0])

	return render(request, 'search.html', {
		'query': query,
		'results': results,
		'total_results': sum(len(v) for k, v in results.items()),
	})
