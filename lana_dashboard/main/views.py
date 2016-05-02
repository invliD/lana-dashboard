from django.conf import settings
from django.shortcuts import render
from lana_dashboard.lana_data.models import AutonomousSystem


def index(request):
	show_map = request.user.is_authenticated() and AutonomousSystem.objects.all().exclude(location_lat=None, location_lng=None)
	return render(request, 'index.html', {
		'show_map': show_map,
	})


def apis(request):
	return render(request, 'lana-apis.js', {
		'mapbox_api_key': settings.LANA_MAPBOX_API_KEY,
	}, content_type='application/javascript')
