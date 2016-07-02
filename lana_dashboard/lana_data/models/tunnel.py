from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from model_utils.managers import InheritanceManager
import netfields

from lana_dashboard.lana_data.models.host import Host


class TunnelEndpoint(models.Model):
	override_internal_ipv4 = netfields.InetAddressField(blank=True, null=True, verbose_name=_("Override internal IPv4 address"))
	dynamic_ipv4 = models.BooleanField(default=False, verbose_name=_("Dynamic IPv4 address"))

	host = models.ForeignKey(Host, models.DO_NOTHING, related_name='tunnel_endpoints', verbose_name=_("Host"))

	objects = netfields.NetManager()

	@property
	def tunnel(self):
		if hasattr(self, 'tunnel1'):
			return self.tunnel1
		if hasattr(self, 'tunnel2'):
			return self.tunnel2
		return None

	@property
	def autonomous_system(self):
		return self.host.autonomous_system

	@property
	def institution(self):
		return self.autonomous_system.institution

	@property
	def internal_ipv4(self):
		return self.override_internal_ipv4 or self.host.tunnel_ipv4

	@property
	def has_geo(self):
		return self.autonomous_system.has_geo

	def can_edit(self, user):
		return self.host.can_edit(user)

	def is_config_complete(self):
		return False


class Tunnel(models.Model):
	MODE_TUN = 'tun'
	MODE_TAP = 'tap'

	mode = models.CharField(max_length=3, choices=(
		(MODE_TUN, 'tun'),
		(MODE_TAP, 'tap'),
	), verbose_name=_("Mode"))
	comment = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Comment"))

	encryption_method = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Encryption method"))
	mtu = models.IntegerField(blank=True, null=True, verbose_name=_("MTU"))

	private = models.BooleanField(default=False, verbose_name=_("Private"))
	endpoint1 = models.OneToOneField(TunnelEndpoint, on_delete=models.CASCADE, related_name='tunnel1', verbose_name=_("Endpoint 1"))
	endpoint2 = models.OneToOneField(TunnelEndpoint, on_delete=models.CASCADE, related_name='tunnel2', verbose_name=_("Endpoint 2"))

	objects = InheritanceManager()

	class Meta:
		ordering = ['endpoint1__host__autonomous_system__as_number', 'endpoint2__host__autonomous_system__as_number']

	@classmethod
	def get_view_qs(cls, user):
		return cls.objects.filter(Q(private=False) | Q(endpoint1__host__autonomous_system__institution__owners=user) | Q(endpoint2__host__autonomous_system__institution__owners=user)).distinct('endpoint1__host__autonomous_system__as_number', 'endpoint2__host__autonomous_system__as_number')

	def __str__(self):
		return "{}-{}".format(self.endpoint1.host.autonomous_system, self.endpoint2.host.autonomous_system)

	@property
	def protocol(self):
		return 'other'

	@property
	def protocol_name(self):
		return _("Other")

	@property
	def real_endpoint1(self):
		return self.endpoint1

	@property
	def real_endpoint2(self):
		return self.endpoint2

	@property
	def has_geo(self):
		return self.endpoint1.has_geo and self.endpoint2.has_geo

	def can_edit(self, user):
		return self.endpoint1.can_edit(user) or self.endpoint2.can_edit(user)

	def prepare_save(self):
		pass

	def supports_config_generation(self):
		return False

	def is_config_complete(self):
		return False

	def get_config_generation_url(self, endpoint_number):
		return None
