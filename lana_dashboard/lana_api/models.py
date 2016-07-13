import binascii
import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _, ungettext_lazy


class Token(models.Model):
	key = models.CharField(_("Key"), max_length=40, primary_key=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, related_name='auth_tokens', verbose_name=_("User"))
	created = models.DateTimeField(_("Created"), auto_now_add=True)

	class Meta:
		verbose_name = ungettext_lazy("Token", "Tokens", 1)
		verbose_name_plural = ungettext_lazy("Token", "Tokens", 2)

	def save(self, *args, **kwargs):
		if not self.key:
			self.key = self.generate_key()
		return super(Token, self).save(*args, **kwargs)

	def generate_key(self):
		return binascii.hexlify(os.urandom(20)).decode()

	def __str__(self):
		return self.key
