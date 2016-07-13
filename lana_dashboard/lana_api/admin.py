from django.contrib import admin

from lana_dashboard.lana_api import models


@admin.register(models.Token)
class HostAdmin(admin.ModelAdmin):
	list_display = ('key', 'user', 'created')
	fields = ('user',)
	ordering = ('-created',)
