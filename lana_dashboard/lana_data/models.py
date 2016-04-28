from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ungettext_lazy, ugettext_lazy as _


class Institution(models.Model):
	name = models.CharField(max_length=255, unique=True, verbose_name=_("Name"))
	code = models.CharField(max_length=8, unique=True, verbose_name=_("Code"))

	owners = models.ManyToManyField(User, related_name='institutions', verbose_name=_("Managers"))

	class Meta:
		verbose_name = ungettext_lazy("Institution", "Institutions", 1)
		verbose_name_plural = ungettext_lazy("Institution", "Institutions", 2)

	def __str__(self):
		return self.name

	def can_edit(self, user):
		return self.owners.filter(id=user.id).exists()


class AutonomousSystem(models.Model):
	as_number = models.IntegerField(primary_key=True, verbose_name=_("AS Number"))
	fqdn = models.CharField(max_length=255, verbose_name=_("FQDN"))
	comment = models.CharField(max_length=255, verbose_name=_("Comment"))

	institution = models.ForeignKey(Institution, related_name='autonomous_systems', verbose_name=_("Institution"))

	class Meta:
		verbose_name = ungettext_lazy("Autonomous System", "Autonomous Systems", 1)
		verbose_name_plural = ungettext_lazy("Autonomous System", "Autonomous Systems", 2)

	def can_edit(self, user):
		return self.institution.can_edit(user)


class IPv4Subnet(models.Model):
	network_address = models.GenericIPAddressField(protocol='IPv4', verbose_name=_("Network Address"))
	subnet_bits = models.IntegerField(verbose_name=_("Subnet Bits"))
	dns_server = models.GenericIPAddressField(protocol='IPv4', verbose_name=_("DNS Server"))
	comment = models.CharField(max_length=255, verbose_name=_("Comment"))

	institution = models.ForeignKey(Institution, related_name='ipv4_subnets', verbose_name=_("Institution"))

	class Meta:
		verbose_name = ungettext_lazy("IPv4 Subnet", "IPv4 Subnets", 1)
		verbose_name_plural = ungettext_lazy("IPv4 Subnet", "IPv4 Subnets", 2)
		unique_together = (
			('network_address', 'subnet_bits'),
		)

	def can_edit(self, user):
		return self.institution.can_edit(user)
