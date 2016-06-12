from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lana_dashboard.lana_data.models.tunnel import Tunnel, TunnelEndpoint


class FastdTunnel(Tunnel):

	@property
	def protocol(self):
		return 'fastd'

	@property
	def protocol_name(self):
		return _("Fastd tunnel")

	@property
	def real_endpoint1(self):
		if isinstance(self.endpoint1, FastdTunnelEndpoint):
			return self.endpoint1
		return self.endpoint1.fastdtunnelendpoint

	@property
	def real_endpoint2(self):
		if isinstance(self.endpoint2, FastdTunnelEndpoint):
			return self.endpoint2
		return self.endpoint2.fastdtunnelendpoint

	def prepare_save(self):
		as1 = self.endpoint1.autonomous_system.as_number
		as2 = self.endpoint2.autonomous_system.as_number
		if not self.real_endpoint1.port and as2 <= 65535:
			self.real_endpoint1.port = as2
			self.real_endpoint1.save()
		if not self.real_endpoint2.port and as1 <= 65535:
			self.real_endpoint2.port = as1
			self.real_endpoint2.save()

	def supports_config_generation(self):
		return True

	def is_config_complete(self):
		return (
			bool(self.encryption_method) and
			bool(self.mtu) and
			self.real_endpoint1.is_config_complete() and
			self.real_endpoint2.is_config_complete()
		)

	def get_config_generation_url(self, endpoint_number):
		return reverse('lana_generator:generate-fastd', kwargs={
			'as_number1': self.endpoint1.autonomous_system.as_number,
			'as_number2': self.endpoint2.autonomous_system.as_number,
			'endpoint_number': endpoint_number,
		})


class VtunTunnel(Tunnel):
	transport = models.CharField(max_length=3, choices=(
		('udp', 'udp'),
		('tcp', 'tcp')
	), verbose_name=_("Transport protocol"))
	compression = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Compression"))

	@property
	def protocol(self):
		return 'vtun'

	@property
	def protocol_name(self):
		return _('VTun tunnel')

	@property
	def real_endpoint1(self):
		if isinstance(self.endpoint1, VtunTunnelEndpoint):
			return self.endpoint1
		else:
			return self.endpoint1.vtuntunnelendpoint

	@property
	def real_endpoint2(self):
		if isinstance(self.endpoint2, VtunTunnelEndpoint):
			return self.endpoint2
		else:
			return self.endpoint2.vtuntunnelendpoint


class FastdTunnelEndpoint(TunnelEndpoint):
	port = models.IntegerField(blank=True, null=True, verbose_name=_("Port"), help_text=_('Defaults to remote AS number if ≤ 65535.'))

	public_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Public key"))

	def is_config_complete(self):
		return (
			(bool(self.host.external_hostname) or bool(self.host.external_ipv4)) and
			bool(self.internal_ipv4) and
			bool(self.port) and
			bool(self.public_key)
		)


class VtunTunnelEndpoint(TunnelEndpoint):
	port = models.IntegerField(blank=True, null=True, verbose_name=_("Port"))
