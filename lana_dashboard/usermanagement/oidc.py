from django.conf import settings
from django.contrib.auth import get_user_model
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class AuthenticationBackend(OIDCAuthenticationBackend):
	def __init__(self, *args, **kwargs):
		# Only set up OIDC backend if it's actually configured.
		if getattr(settings, 'OIDC_RP_CLIENT_ID', None) is not None:
			super(AuthenticationBackend, self).__init__(self, *args, **kwargs)
		else:
			self.UserModel = get_user_model()

	def filter_users_by_claims(self, claims):
		username = self.get_username(claims)
		if not username:
			return self.UserModel.objects.none()

		try:
			user = get_user_model().objects.get(username=username)
			return [user]

		except get_user_model().DoesNotExist:
			return self.UserModel.objects.none()

	def get_username(self, claims):
		return claims.get('sub')

	def create_user(self, claims):
		user = super(AuthenticationBackend, self).create_user(claims)

		user.first_name = claims.get('given_name', '')
		user.last_name = claims.get('family_name', '')
		user.save()

		return user

	def update_user(self, user, claims):
		user.email = claims.get('email')
		user.first_name = claims.get('given_name', '')
		user.last_name = claims.get('family_name', '')
		user.save()

		return user
