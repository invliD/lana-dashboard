from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from lana_dashboard.usermanagement.models import ContactInformation


class ContactInformationInline(admin.StackedInline):
	model = ContactInformation
	can_delete = False


class UserAdmin(BaseUserAdmin):
	inlines = (ContactInformationInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
