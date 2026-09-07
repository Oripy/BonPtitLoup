from django.test import TestCase
from django.urls import reverse

from .models import CustomUser


class LoginViewTests(TestCase):
	def setUp(self):
		CustomUser.objects.create_user(
			username='parent1',
			email='parent@example.com',
			password='1234',
		)

	def test_login_with_email(self):
		response = self.client.post(
			reverse('accounts:login'),
			{'identifier': 'parent@example.com', 'password': '1234'},
		)

		self.assertRedirects(response, reverse('home'))
		self.assertTrue(response.wsgi_request.user.is_authenticated)

	def test_login_with_username(self):
		response = self.client.post(
			reverse('accounts:login'),
			{'identifier': 'parent1', 'password': '1234'},
		)

		self.assertRedirects(response, reverse('home'))
		self.assertTrue(response.wsgi_request.user.is_authenticated)
