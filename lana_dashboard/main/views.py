from django.conf import settings
from django.shortcuts import render


def index(request):
	return render(request, 'index.html')


def apis(request):
	return render(request, 'lana-apis.js', {
		'mapbox_api_key': settings.LANA_MAPBOX_API_KEY,
	}, content_type='application/javascript')
