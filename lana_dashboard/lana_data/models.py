from django.contrib.auth.models import User
from django.db import models


class Institution(models.Model):
	name = models.CharField(max_length=255, unique=True)
	code = models.CharField(max_length=8, unique=True)

	owners = models.ManyToManyField(User, related_name='institutions')

	def can_edit(self, user):
		return self.owners.filter(id=user.id).exists()


class AutonomousSystem(models.Model):
	as_number = models.IntegerField(primary_key=True)
	fqdn = models.CharField(max_length=255)
	comment = models.CharField(max_length=255)

	institution = models.ForeignKey(Institution, related_name='autonomous_systems')

	def can_edit(self, user):
		return self.institution.can_edit(user)


class IPv4Subnet(models.Model):
	network_address = models.GenericIPAddressField(protocol='IPv4')
	subnet_bits = models.IntegerField()
	dns_server = models.GenericIPAddressField(protocol='IPv4')
	comment = models.CharField(max_length=255)

	institution = models.ForeignKey(Institution, related_name='ipv4_subnets')

	class Meta:
		unique_together = (
			('network_address', 'subnet_bits'),
		)

	def can_edit(self, user):
		return self.institution.can_edit(user)
