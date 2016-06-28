from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from .validators import validate_pgp_key


class ContactInformation(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, models.CASCADE, primary_key=True, related_name='contact_information', verbose_name=_("Contact Information"))

	show_email = models.BooleanField(default=False, verbose_name=_("Show email"))
	skype_user = models.CharField(max_length=64, blank=True, verbose_name=_("Skype User"))
	xmpp_address = models.CharField(max_length=255, blank=True, verbose_name=_("XMPP address"))
	pgp_key = models.TextField(blank=True, validators=[validate_pgp_key], verbose_name=_("PGP Key"))
	additional_text = models.TextField(blank=True, verbose_name=_("Additional Text"))

	class Meta:
		verbose_name = ungettext_lazy("Contact Information", "Contact Information", 1)
		verbose_name_plural = ungettext_lazy("Contact Information", "Contact Information", 2)

	def __str__(self):
		return _("%s's Contact Information") % self.user.get_full_name()
