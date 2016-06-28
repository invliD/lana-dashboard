from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from pgp import read_key


def validate_pgp_key(value):
	try:
		read_key(value, True)
	except ValueError as e:
		raise ValidationError(_('This is not a valid PGP key'), code='invalid') from e
