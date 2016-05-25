from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from colorfield.fields import ColorField
from model_utils.managers import InheritanceManager
import netfields


class Institution(models.Model):
	name = models.CharField(max_length=255, unique=True, verbose_name=_("Name"))
	code = models.CharField(max_length=8, unique=True, verbose_name=_("Code"))
	abuse_email = models.EmailField(blank=True, verbose_name=_("Abuse Email"))
	color = ColorField(default="#808080", verbose_name=_("Institution Color"))

	owners = models.ManyToManyField(User, related_name='institutions', verbose_name=_("Managers"))

	class Meta:
		ordering = ['code']
		verbose_name = ungettext_lazy("Institution", "Institutions", 1)
		verbose_name_plural = ungettext_lazy("Institution", "Institutions", 2)

	@classmethod
	def get_view_qs(cls, user):
		return cls.objects

	def __str__(self):
		return self.name

	def can_edit(self, user):
		return self.owners.filter(id=user.id).exists()


class AutonomousSystem(models.Model):
	as_number = models.BigIntegerField(unique=True, verbose_name=_("AS Number"))
	fqdn = models.CharField(max_length=255, verbose_name=_("FQDN"))
	comment = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Comment"))
	location_lat = models.FloatField(blank=True, null=True, verbose_name=_("Latitude"))
	location_lng = models.FloatField(blank=True, null=True, verbose_name=_("Longitude"))

	private = models.BooleanField(default=False, verbose_name=_("Private"))
	institution = models.ForeignKey(Institution, related_name='autonomous_systems', verbose_name=_("Institution"))

	class Meta:
		ordering = ['as_number']
		verbose_name = ungettext_lazy("Autonomous System", "Autonomous Systems", 1)
		verbose_name_plural = ungettext_lazy("Autonomous System", "Autonomous Systems", 2)

	@classmethod
	def get_view_qs(cls, user):
		return cls.objects.filter(Q(private=False) | Q(institution__owners=user))

	def __str__(self):
		return "AS{}".format(self.as_number)

	def can_edit(self, user):
		return self.institution.can_edit(user)


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
		return cls.objects.filter(Q(private=False) | Q(institution__owners=user))

	def __str__(self):
		return str(self.network)

	def can_edit(self, user):
		return self.institution.can_edit(user)


class TunnelEndpoint(models.Model):
	external_hostname = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("External hostname"))
	external_ipv4 = netfields.InetAddressField(blank=True, null=True, verbose_name=_("External IPv4 address"))
	internal_ipv4 = netfields.InetAddressField(blank=True, null=True, verbose_name=_("Internal IPv4 address"))

	autonomous_system = models.ForeignKey(AutonomousSystem, related_name='tunnel_endpoints', verbose_name=_("Autonomous System"))

	objects = netfields.NetManager()

	@property
	def tunnel(self):
		if hasattr(self, 'tunnel1'):
			return self.tunnel1
		if hasattr(self, 'tunnel2'):
			return self.tunnel2
		return None

	def can_edit(self, user):
		return self.autonomous_system.can_edit(user)

	def is_config_complete(self):
		return False


class FastdTunnelEndpoint(TunnelEndpoint):
	port = models.IntegerField(blank=True, null=True, verbose_name=_("Port"), help_text=_('Defaults to remote AS number if ≤ 65535.'))

	public_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Public key"))

	def is_config_complete(self):
		return ((bool(self.external_hostname) or bool(self.external_ipv4)) and
				bool(self.internal_ipv4) and
				bool(self.port) and
				bool(self.public_key))


class VtunTunnelEndpoint(TunnelEndpoint):
	port = models.IntegerField(blank=True, null=True, verbose_name=_("Port"))


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
		ordering = ['endpoint1__autonomous_system__as_number', 'endpoint2__autonomous_system__as_number']

	@classmethod
	def get_view_qs(cls, user):
		return cls.objects.filter(Q(private=False) | Q(endpoint1__autonomous_system__institution__owners=user) | Q(endpoint2__autonomous_system__institution__owners=user))

	def __str__(self):
		return "{}-{}".format(self.endpoint1.autonomous_system, self.endpoint2.autonomous_system)

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
		return (bool(self.encryption_method) and
			bool(self.mtu) and
			self.real_endpoint1.is_config_complete() and
			self.real_endpoint2.is_config_complete())

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
