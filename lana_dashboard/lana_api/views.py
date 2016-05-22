from ipaddress import ip_interface

from django.http import Http404
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from lana_dashboard.lana_api.serializers import IPv4SubnetSerializer
from lana_dashboard.lana_data.models import IPv4Subnet


class WhoisViewSet(ViewSet):
	"""
	Allows querying LANA for a given IP address or network. If found, the smallest subnet that contains the given
	address or network will be returned, including its Institution.
	"""
	lookup_value_regex = '[0-9\./]+'

	def retrieve(self, request, pk=None, format=None):
		try:
			interface = ip_interface(pk)
			subnets = IPv4Subnet.objects.filter(network__net_contains_or_equals=str(interface.network)).order_by('-network')[:1].select_related('institution')
			if not subnets.exists():
				raise Http404
			subnet = subnets.first()
			serializer = IPv4SubnetSerializer(subnet)
			return Response(serializer.data)
		except ValueError:
			raise Http404
