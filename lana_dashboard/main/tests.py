from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class IntegrationTestCase(TestCase):

	def setUp(self):
		self.user = User(username='admin', password=make_password('pwd'))
		self.user.save()

		self.client = Client()
		self.client.login(username='admin', password='pwd')


class MainIntegrationTests(IntegrationTestCase):
	def test_unauthenticated_index(self):
		client = Client()
		response = client.get(reverse('main-index'))
		self.assertEqual(response.status_code, 200)

	def test_authenticated_index(self):
		response = self.client.get(reverse('main-index'))
		self.assertEqual(response.status_code, 200)
