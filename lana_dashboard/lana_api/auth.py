from functools import reduce

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission


class StaticTokenWhoisAuthentication(BaseAuthentication):

	def authenticate(self, request):
		token = request.META.get('HTTP_X_LANA_TOKEN')
		if not token:
			return None

		if not hasattr(settings, 'LANA_WHOIS_API_TOKEN'):
			raise AuthenticationFailed
		settings_token = settings.LANA_WHOIS_API_TOKEN
		if not settings_token:
			raise AuthenticationFailed
		if token == settings_token:
			return None, 'lana_api.whois'
		raise AuthenticationFailed


def and_permission(permissions):
	class AndPermission(BasePermission):
		def has_permission(self, request, view):
			if len(permissions) == 1:
				return permissions[0].has_permission(permissions[0], request, view)

			def combine(a, b):
				return a.has_permission(request, view) and b.has_permission(request, view)
			return reduce(combine, permissions)

	return [AndPermission]


def or_permission(permissions):
	class OrPermission(BasePermission):
		def has_permission(self, request, view):
			if len(permissions) == 1:
				return permissions[0].has_permission(permissions[0], request, view)

			def combine(a, b):
				return a.has_permission(a, request, view) or b.has_permission(b, request, view)
			return reduce(combine, permissions)

	return [OrPermission]


class StaticTokenWhoisPermission(BasePermission):

	def has_permission(self, request, view):
		if request.auth == 'lana_api.whois':
			return True
		return False
