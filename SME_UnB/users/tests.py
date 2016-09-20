from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
import unittest

class TestLoginView(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_getting_page_login(self):
        response = self.client.post(
            '/accounts/login/',
            {"username": 'temporary', 'password': 'temporary' }
        )

        self.assertEqual(200, response.status_code)

    def test_getting_wrong_page_login(self):
        response = self.client.post(
            '/accounts/ladfogin/',
            {"username": 'temporary', 'password': 'temporary' }
        )

        self.assertEqual(404, response.status_code)

    def test_getting_page_home(self):
        response = self.client.get(
            '/accounts/dashboard/',
        )

        self.assertEqual(302, response.status_code)

    def test_getting_wrong_page_home(self):
        response = self.client.get(
            '/accounts/dash/',
        )

        self.assertEqual(404, response.status_code)
