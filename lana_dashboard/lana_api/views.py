from ipaddress import ip_interface

from django.db.models import Q
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
from lana_dashboard.lana_api.serializers import (
	FastdTunnelEndpointSerializer,
	FastdTunnelSerializer,
	IPv4SubnetSerializer,
	VtunTunnelEndpointSerializer,
	VtunTunnelSerializer,
)
from lana_dashboard.lana_data.models import FastdTunnel, Host, IPv4Subnet, VtunTunnel
from lana_dashboard.lana_data.utils import get_object_for_view_or_404, list_objects_for_view


def get_view_name(view_cls, suffix=None):
	if view_cls.__name__ == 'APIRoot':
		return 'API'
	elif hasattr(view_cls, 'get_breadcrumb_name'):
		return view_cls.get_breadcrumb_name()
	else:
		return base_get_view_name(view_cls, suffix=suffix)


class HieraViewSet(ViewSet):
	"""
	Allows querying LANA for a given FQDN. If a host with that FQDN is found, a hiera-compatible JSON object will be
	returned, including all Tunnels.
	"""
	lookup_value_regex = '.+'

	@classmethod
	def get_breadcrumb_name(cls):
		return 'Hiera'

	def serialize_tunnel(self, tunnel_serializer_cls, tunnel_endpoint_serializer_cls, tunnel, host):
		serialized_tunnel = tunnel_serializer_cls(tunnel).data

		local_endpoint = tunnel.real_endpoint1
		remote_endpoint = tunnel.real_endpoint2
		if remote_endpoint.host.fqdn == host.fqdn:
			local_endpoint, remote_endpoint = remote_endpoint, local_endpoint

		serialized_tunnel['local_endpoint'] = tunnel_endpoint_serializer_cls(local_endpoint).data
		serialized_tunnel['remote_endpoint'] = tunnel_endpoint_serializer_cls(remote_endpoint).data
		return serialized_tunnel

	def retrieve(self, request, pk=None, format=None):
		host = get_object_for_view_or_404(Host, request, fqdn=pk)

		fastd_tunnels = list_objects_for_view(FastdTunnel, request, Q(endpoint1__host=host) | Q(endpoint2__host=host)).select_related(
			'endpoint1',
			'endpoint2',
			'endpoint1__fastdtunnelendpoint',
			'endpoint2__fastdtunnelendpoint',
			'endpoint1__fastdtunnelendpoint__host',
			'endpoint2__fastdtunnelendpoint__host',
			'endpoint1__fastdtunnelendpoint__tunnel1',
			'endpoint2__fastdtunnelendpoint__tunnel1',
			'endpoint1__fastdtunnelendpoint__tunnel2',
			'endpoint2__fastdtunnelendpoint__tunnel2',
		)
		serialized_fastd_tunnels = [self.serialize_tunnel(FastdTunnelSerializer, FastdTunnelEndpointSerializer, t, host) for t in fastd_tunnels]

		vtun_tunnels = list_objects_for_view(VtunTunnel, request, Q(endpoint1__host=host) | Q(endpoint2__host=host)).select_related(
			'endpoint1',
			'endpoint2',
			'endpoint1__vtuntunnelendpoint',
			'endpoint2__vtuntunnelendpoint',
			'endpoint1__vtuntunnelendpoint__host',
			'endpoint2__vtuntunnelendpoint__host',
			'endpoint1__vtuntunnelendpoint__tunnel1',
			'endpoint2__vtuntunnelendpoint__tunnel1',
			'endpoint1__vtuntunnelendpoint__tunnel2',
			'endpoint2__vtuntunnelendpoint__tunnel2',
		)
		serialized_vtun_tunnels = [self.serialize_tunnel(VtunTunnelSerializer, VtunTunnelEndpointSerializer, t, host) for t in vtun_tunnels]

		return Response({
			'lana': {
				'tunnels': {
					'fastd': serialized_fastd_tunnels,
					'vtun': serialized_vtun_tunnels,
				}
			},
		})


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
			if len(subnets) == 0:
				raise Http404
			subnet = subnets.first()
			serializer = IPv4SubnetSerializer(subnet)
			return Response(serializer.data)
		except ValueError:
			raise Http404
