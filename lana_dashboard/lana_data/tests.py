import json

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from lana_dashboard.lana_data.models import AutonomousSystem, Institution, IPv4Subnet


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
		self.assertEqual(response.status_code, 403)

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
