from django.test import TestCase
from django.test import Client
import unittest

class TestLoginView(unittest.TestCase):
    def test_correct_login(self):
        client = Client()
        response = client.post(
            '/accounts/login/',
            {"username": 'admin', 'password': 'tiago1107' }
        )

        self.assertEqual(200, response.status_code)
