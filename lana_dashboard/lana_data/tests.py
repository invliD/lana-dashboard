import json

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from lana_dashboard.lana_data.models import AutonomousSystem, Host, Institution, IPv4Subnet, Tunnel, TunnelEndpoint


class IntegrationTestCase(TestCase):

	def setUp(self):
		self.user = User(username='admin', password=make_password('pwd'))
		self.user.save()

		self.client = Client()
		self.client.login(username='admin', password='pwd')

		self.i1 = Institution(code='t1', name='Test Institution 1', abuse_email='abuse@example.net')
		self.i1.save()
		self.i1.owners.add(self.user)
		self.i1.save()
		Institution(code='t2', name='Test Institution 2').save()


class InstitutionIntegrationTests(IntegrationTestCase):

	def test_list_institutions(self):
		response = self.client.get(reverse('lana_data:institutions'))
		self.assertEqual(response.status_code, 200)

	def test_delete_institution_get(self):
		response = self.client.get(reverse('lana_data:institution-delete', kwargs={'code': 't1'}))
		self.assertEqual(response.status_code, 405)

	def test_delete_institution_as(self):
		AutonomousSystem(as_number=1, institution=self.i1).save()
		response = self.client.post(reverse('lana_data:institution-delete', kwargs={'code': 't1'}))
		self.assertEqual(response.status_code, 302)
		Institution.objects.get(code='t1')

	def test_delete_institution_ipv4(self):
		IPv4Subnet(network='10.0.0.0/8', institution=self.i1).save()
		response = self.client.post(reverse('lana_data:institution-delete', kwargs={'code': 't1'}))
		self.assertEqual(response.status_code, 302)
		Institution.objects.get(code='t1')

	def test_delete_institution_post(self):
		response = self.client.post(reverse('lana_data:institution-delete', kwargs={'code': 't1'}))
		self.assertEqual(response.status_code, 302)
		with self.assertRaises(Institution.DoesNotExist):
			Institution.objects.get(code='t1')

	def test_create_institution_form(self):
		response = self.client.get(reverse('lana_data:institution-create'))
		self.assertEqual(response.status_code, 200)

	def test_create_institution_post(self):
		response = self.client.post(reverse('lana_data:institution-create'), {
			'code': 't3',
			'name': 'Created Institution',
			'color': '#000000',
			'abuse_email': 'abuse@example.com',
		})
		self.assertEqual(response.status_code, 302)
		institutions = Institution.objects.all()
		self.assertEqual(len(institutions), 3)

	def test_edit_institution_form(self):
		response = self.client.get(reverse('lana_data:institution-edit', kwargs={'code': 't1'}))
		self.assertEqual(response.status_code, 200)

	def test_edit_institution_post(self):
		response = self.client.post(reverse('lana_data:institution-edit', kwargs={'code': 't1'}), {
			'code': self.i1.code,
			'name': 'Edited Institution',
			'color': self.i1.color,
			'abuse_email': self.i1.abuse_email,
		})
		self.assertEqual(response.status_code, 302)
		institution = Institution.objects.get(code='t1')
		self.assertEqual(institution.name, 'Edited Institution')

	def test_show_institution(self):
		response = self.client.get(reverse('lana_data:institution-details', kwargs={'code': 't1'}))
		self.assertEqual(response.status_code, 200)

	def test_list_institution_autonomous_systems_web(self):
		response = self.client.get(reverse('lana_data:institution-autonomous_systems', kwargs={'code': 't1'}))
		self.assertEqual(response.status_code, 404)

	def test_list_institution_autonomous_systems_geojson(self):
		response = self.client.get(reverse('lana_data:institution-autonomous_systems', kwargs={'code': 't1'}), HTTP_ACCEPT='application/vnd.geo+json')
		self.assertEqual(response.status_code, 200)
		json.loads(response.content.decode())

	def test_list_institution_tunnels_web(self):
		response = self.client.get(reverse('lana_data:institution-tunnels', kwargs={'code': 't1'}))
		self.assertEqual(response.status_code, 404)

	def test_list_institution_tunnels_geojson(self):
		response = self.client.get(reverse('lana_data:institution-tunnels', kwargs={'code': 't1'}), HTTP_ACCEPT='application/vnd.geo+json')
		self.assertEqual(response.status_code, 200)
		json.loads(response.content.decode())


class AutonomousSystemIntegrationTextx(IntegrationTestCase):

	def setUp(self):
		super().setUp()

		self.as1 = AutonomousSystem(as_number=1234, institution=self.i1)
		self.as1.save()
		self.as2 = AutonomousSystem(as_number=5678, institution=self.i1)
		self.as2.save()
		self.as3 = AutonomousSystem(as_number=9012, institution=self.i1)
		self.as3.save()

		h1 = Host(fqdn='host1.example.com', autonomous_system=self.as2)
		h1.save()
		h2 = Host(fqdn='host2.example.com', autonomous_system=self.as3)
		h2.save()
		te1 = TunnelEndpoint(host=h1)
		te1.save()
		te2 = TunnelEndpoint(host=h2)
		te2.save()
		Tunnel(mode='tun', endpoint1=te1, endpoint2=te2).save()
		Tunnel(mode='tun', endpoint1=te2, endpoint2=te1).save()

	def test_list_autonomous_systems_web(self):
		response = self.client.get(reverse('lana_data:autonomous_systems'))
		self.assertEqual(response.status_code, 200)

	def test_list_autonomous_systems_geojson(self):
		response = self.client.get(reverse('lana_data:autonomous_systems'), HTTP_ACCEPT='application/vnd.geo+json')
		self.assertEqual(response.status_code, 200)
		json.loads(response.content.decode())

	def test_delete_autonomous_system_get(self):
		response = self.client.get(reverse('lana_data:autonomous_system-delete', kwargs={'as_number': 1234}))
		self.assertEqual(response.status_code, 405)

	def test_delete_autonomous_system_host(self):
		Host(fqdn='host.example.com', autonomous_system=self.as1).save()
		response = self.client.post(reverse('lana_data:autonomous_system-delete', kwargs={'as_number': 1234}))
		self.assertEqual(response.status_code, 302)
		AutonomousSystem.objects.get(as_number=1234)

	def test_delete_autonomous_system_post(self):
		response = self.client.post(reverse('lana_data:autonomous_system-delete', kwargs={'as_number': 1234}))
		self.assertEqual(response.status_code, 302)
		with self.assertRaises(AutonomousSystem.DoesNotExist):
			AutonomousSystem.objects.get(as_number=1234)

	def test_create_autonomous_system_form(self):
		response = self.client.get(reverse('lana_data:autonomous_system-create'))
		self.assertEqual(response.status_code, 200)

	def test_create_autonomous_system_form_preselect(self):
		response = self.client.get(reverse('lana_data:autonomous_system-create'), data={
			'institution': self.i1.code,
		})
		self.assertEqual(response.status_code, 200)

	def test_create_autonomous_system_create(self):
		response = self.client.post(reverse('lana_data:autonomous_system-create'), {
			'as_number': '2345',
			'institution': self.i1.id,
		})
		self.assertEqual(response.status_code, 302)
		autonomous_systems = AutonomousSystem.objects.all()
		self.assertEqual(len(autonomous_systems), 4)

	def test_edit_autonomous_system_form(self):
		response = self.client.get(reverse('lana_data:autonomous_system-edit', kwargs={'as_number': 1234}))
		self.assertEqual(response.status_code, 200)

	def test_edit_autonomous_system_post(self):
		response = self.client.post(reverse('lana_data:autonomous_system-edit', kwargs={'as_number': 1234}), {
			'as_number': 3456,
			'institution': self.i1.id,
		})
		self.assertEqual(response.status_code, 302)
		autonomous_system = AutonomousSystem.objects.get(as_number=3456)
		self.assertEqual(autonomous_system.as_number, 3456)

	def test_show_autonomous_system_web(self):
		response = self.client.get(reverse('lana_data:autonomous_system-details', kwargs={'as_number': 5678}))
		self.assertEqual(response.status_code, 200)

	def test_show_autonomous_system_geojson(self):
		response = self.client.get(reverse('lana_data:autonomous_system-details', kwargs={'as_number': 1234}), HTTP_ACCEPT='application/vnd.geo+json')
		self.assertEqual(response.status_code, 200)
		json.loads(response.content.decode())
