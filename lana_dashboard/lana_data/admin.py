from django.contrib import admin

from lana_dashboard.lana_data import models

admin.site.register(models.Institution)
admin.site.register(models.AutonomousSystem)
admin.site.register(models.IPv4Subnet)
