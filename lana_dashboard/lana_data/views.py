from django.shortcuts import render

from lana_dashboard.lana_data.models import Institution


def list_institutions(request):
	institutions = Institution.objects.all()

	return render(request, 'institutions_list.html', {
		'institutions': institutions,
	})


def list_autonomous_systems(request):
	pass


def list_ipv4(request):
	pass
