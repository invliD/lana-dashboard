from ipaddress import ip_interface

from django.http import Http404
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import get_view_name as base_get_view_name
from rest_framework.viewsets import ViewSet

from lana_dashboard.lana_api.auth import (
	and_permission,
	or_permission,
	StaticTokenWhoisAuthentication,
	StaticTokenWhoisPermission,
)

from lana_dashboard.lana_api.serializers import IPv4SubnetSerializer
from lana_dashboard.lana_data.models import IPv4Subnet
from lana_dashboard.lana_data.utils import list_objects_for_view


def get_view_name(view_cls, suffix=None):
	if view_cls.__name__ == 'APIRoot':
		return 'API'
	elif hasattr(view_cls, 'get_breadcrumb_name'):
		return view_cls.get_breadcrumb_name()
	else:
		return base_get_view_name(view_cls, suffix=suffix)


class WhoisViewSet(ViewSet):
	"""
	Allows querying LANA for a given IP address or network. If found, the smallest subnet that contains the given
	address or network will be returned, including its Institution.
	"""
	authentication_classes = [StaticTokenWhoisAuthentication,] + api_settings.DEFAULT_AUTHENTICATION_CLASSES
	permission_classes = or_permission([StaticTokenWhoisPermission,] + and_permission(api_settings.DEFAULT_PERMISSION_CLASSES))
	lookup_value_regex = '[0-9\./]+'

	@classmethod
	def get_breadcrumb_name(cls):
		return 'Whois'

	def retrieve(self, request, pk=None, format=None):
		try:
			interface = ip_interface(pk)
			subnets = list_objects_for_view(IPv4Subnet, request, network__net_contains_or_equals=str(interface.network)).order_by('-network')[:1].select_related('institution')
			if not subnets.exists():
				raise Http404
			subnet = subnets.first()
			serializer = IPv4SubnetSerializer(subnet)
			return Response(serializer.data)
		except ValueError:
			raise Http404
