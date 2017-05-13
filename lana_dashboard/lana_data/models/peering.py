from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, ungettext_lazy
from model_utils.managers import InheritanceManager

from lana_dashboard.lana_data.models.tunnel import Tunnel


class Peering(models.Model):
	bfd_enabled = models.BooleanField(default=False, verbose_name=_("BFD enabled"))

	private = models.BooleanField(default=False, verbose_name=_("Private"))

	objects = InheritanceManager()

	class Meta:
		ordering = ['tunnelpeering__tunnel__endpoint1__host__autonomous_system__as_number', 'tunnelpeering__tunnel__endpoint2__host__autonomous_system__as_number']
		verbose_name = ungettext_lazy("Peering", "Peerings", 1)
		verbose_name_plural = ungettext_lazy("Peering", "Peerings", 2)

	@classmethod
	def get_view_qs(cls, user):
		return cls.objects.filter(Q(private=False) | Q(tunnelpeering__tunnel__endpoint1__host__autonomous_system__institution__owners=user) | Q(tunnelpeering__tunnel__endpoint2__host__autonomous_system__institution__owners=user)).distinct('tunnelpeering__tunnel__endpoint1__host__autonomous_system__as_number', 'tunnelpeering__tunnel__endpoint2__host__autonomous_system__as_number')

	def __str__(self):
		return "{}-{}".format(self.host1.autonomous_system, self.host2.autonomous_system)


class TunnelPeering(Peering):
	tunnel = models.OneToOneField(Tunnel, on_delete=models.CASCADE, related_name='peering', verbose_name=_("Tunnel"))

	class Meta:
		ordering = ['tunnel__endpoint1__host__autonomous_system__as_number', 'tunnel__endpoint2__host__autonomous_system__as_number']
		verbose_name = ungettext_lazy("Tunnel Peering", "Tunnel Peerings", 1)
		verbose_name_plural = ungettext_lazy("Tunnel Peering", "Tunnel Peerings", 2)

	def can_edit(self, user):
		return self.tunnel.can_edit(user)

	@property
	def host1(self):
		return self.tunnel.endpoint1.host

	@property
	def internal_ipv4_1(self):
		return self.tunnel.endpoint1.internal_ipv4

	@property
	def host2(self):
		return self.tunnel.endpoint2.host

	@property
	def internal_ipv4_2(self):
		return self.tunnel.endpoint2.internal_ipv4
