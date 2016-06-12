from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from lana_dashboard.lana_data.models.institution import Institution


class AutonomousSystem(models.Model):
	as_number = models.BigIntegerField(unique=True, verbose_name=_("AS Number"))
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
		return cls.objects.filter(Q(private=False) | Q(institution__owners=user)).distinct('as_number')

	@property
	def has_geo(self):
		return self.location_lat is not None and self.location_lng is not None

	def __str__(self):
		return "AS{}".format(self.as_number)

	def can_view(self, user):
		return not self.private or self.institution.owners.filter(id=user.id).exists()

	def can_edit(self, user):
		return self.institution.can_edit(user)
