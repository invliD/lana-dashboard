from django.shortcuts import render

from lana_dashboard.lana_data.models import AutonomousSystem, Institution, IPv4Subnet


def list_institutions(request):
	institutions = Institution.objects.all()

	return render(request, 'institutions_list.html', {
		'header_active': 'institutions',
		'institutions': institutions,
	})


def list_autonomous_systems(request):
	autonomous_systems = AutonomousSystem.objects.all()

	return render(request, 'autonomous_systems_list.html', {
		'header_active': 'autonomous_systems',
		'autonomous_systems': autonomous_systems,
	})


def list_ipv4(request):
	subnets = IPv4Subnet.objects.all()

	return render(request, 'ipv4_list.html', {
		'header_active': 'ipv4',
		'subnets': subnets,
	})
