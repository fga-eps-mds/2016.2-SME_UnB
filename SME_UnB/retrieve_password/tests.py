from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
import unittest

class TestLoginView(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.user, self.created = User.objects.get_or_create(
        username='testuser'
        )
        self.user.set_password('12345')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.email = "admin@admin.com"
        self.user.save()

    def test_is_reseting_password(self):
        old_pass = self.user.password

        self.client.post(
            '/retrieve_password/reset_password/',
            {
                'pass': '123456',
                'confirm_pass': '123456',
                'email': 'test@email.com'
            }
        )
        new_pass = User.objects.get(username='testuser')

        password_has_changed = True if old_pass is not new_pass else False

        self.assertTrue(password_has_changed)
