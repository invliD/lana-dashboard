from colorfield.fields import ColorField
from django.contrib.auth.models import User
from django.contrib.postgres.fields import BigIntegerRangeField
from django.db import models
from django.utils.translation import ugettext_lazy as _, ungettext_lazy


class Institution(models.Model):
	name = models.CharField(max_length=255, unique=True, verbose_name=_("Name"))
	code = models.CharField(max_length=8, unique=True, verbose_name=_("Code"))
	as_range = BigIntegerRangeField(blank=True, null=True, verbose_name=_("AS Range"))
	abuse_email = models.EmailField(verbose_name=_("Abuse Email"))
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
