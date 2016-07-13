from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LanaApiConfig(AppConfig):
    name = 'lana_dashboard.lana_api'
    verbose_name = _("LANA API")
