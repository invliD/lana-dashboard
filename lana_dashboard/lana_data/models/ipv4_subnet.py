from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, ungettext_lazy
import netfields

from lana_dashboard.lana_data.models.institution import Institution


class IPv4Subnet(models.Model):
	network = netfields.CidrAddressField(unique=True, verbose_name=_("Network"))
	dns_server = netfields.InetAddressField(blank=True, null=True, verbose_name=_("DNS Server"))
	comment = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Comment"))

	private = models.BooleanField(default=False, verbose_name=_("Private"))
	institution = models.ForeignKey(Institution, related_name='ipv4_subnets', verbose_name=_("Institution"))

	objects = netfields.NetManager()

	class Meta:
		ordering = ['network']
		verbose_name = ungettext_lazy("IPv4 Subnet", "IPv4 Subnets", 1)
		verbose_name_plural = ungettext_lazy("IPv4 Subnet", "IPv4 Subnets", 2)

	@classmethod
	def get_view_qs(cls, user):
		return cls.objects.filter(Q(private=False) | Q(institution__owners=user)).distinct('network')

	def __str__(self):
		return str(self.network)

	def can_edit(self, user):
		return self.institution.can_edit(user)
