from django.conf import settings
from django.shortcuts import render

from lana_dashboard.lana_data.models import AutonomousSystem
from lana_dashboard.lana_data.utils import list_objects_for_view


def index(request):
	show_map = request.user.is_authenticated and list_objects_for_view(AutonomousSystem, request, location_lat__isnull=False, location_lng__isnull=False).exists()
	return render(request, 'index.html', {
		'show_map': show_map,
	})


def apis(request):
	return render(request, 'lana-apis.js', {
		'mapbox_api_key': settings.LANA_MAPBOX_API_KEY,
	}, content_type='application/javascript')
