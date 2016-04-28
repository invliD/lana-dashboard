from django.shortcuts import render

from lana_dashboard.lana_data.models import AutonomousSystem, Institution


def list_institutions(request):
	institutions = Institution.objects.all()

	return render(request, 'institutions_list.html', {
		'institutions': institutions,
	})


def list_autonomous_systems(request):
	autonomous_systems = AutonomousSystem.objects.all()

	return render(request, 'autonomous_systems_list.html', {
		'autonomous_systems': autonomous_systems,
	})


def list_ipv4(request):
	pass
