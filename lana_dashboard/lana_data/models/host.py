from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, ungettext_lazy
import netfields

from lana_dashboard.lana_data.models.autonomous_system import AutonomousSystem


class Host(models.Model):
	fqdn = models.CharField(unique=True, max_length=255, verbose_name=_("FQDN"))
	external_hostname = models.CharField(max_length=255, blank=True, verbose_name=_("External hostname"))
	external_ipv4 = netfields.InetAddressField(blank=True, null=True, verbose_name=_("External IPv4 address"))
	internal_ipv4 = netfields.InetAddressField(blank=True, null=True, verbose_name=_("Internal IPv4 address"))
	tunnel_ipv4 = netfields.InetAddressField(blank=True, null=True, verbose_name=_("Tunnel IPv4 address"))
	comment = models.CharField(max_length=255, blank=True, verbose_name=_("Comment"))

	private = models.BooleanField(default=False, verbose_name=_("Private"))
	autonomous_system = models.ForeignKey(AutonomousSystem, models.DO_NOTHING, related_name='hosts', verbose_name=_("Autonomous System"))

	objects = netfields.NetManager()

	class Meta:
		ordering = ['fqdn']
		verbose_name = ungettext_lazy("Host", "Hosts", 1)
		verbose_name_plural = ungettext_lazy("Host", "Hosts", 2)

	@classmethod
	def get_view_qs(cls, user):
		return cls.objects.filter(Q(private=False) | Q(autonomous_system__institution__owners=user)).distinct('fqdn')

	@property
	def institution(self):
		return self.autonomous_system.institution

	@property
	def has_geo(self):
		return self.autonomous_system.has_geo

	def __str__(self):
		return self.fqdn

	def can_edit(self, user):
		return self.autonomous_system.can_edit(user)
