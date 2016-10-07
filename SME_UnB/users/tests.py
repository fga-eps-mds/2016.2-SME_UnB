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

    def test_getting_wrong_page_edit_user(self):
        response = self.client.get(
            'accounts/edit_user/1/',
        )

        self.assertEqual(404, response.status_code)

    def test_getting_list_user_edit(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get( '/accounts/list_user_edit/')

        self.assertEqual(200, response.status_code)

    def test_getting_list_user_delete(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get( '/accounts/list_user_delete/')

        self.assertEqual(200, response.status_code)

    def test_getting_user_register(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get( '/accounts/register/')

        self.assertEqual(200, response.status_code)

    def test_post_user_register(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.post(
            '/accounts/register/',
            {
                'username': 'testsecond',
                'password': '123456',
                'confirmPassword': '123456',
                'first_name': 'Testsecond',
                'last_name': 'Lastname',
                'email': 'test@email.com'
            }
        )

        self.assertEqual(200, response.status_code)

    def test_post_user_register_wrong_name(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.post(
            '/accounts/register/',
            {
                'username': 'testsecond',
                'password': '123456',
                'confirmPassword': '123456',
                'first_name': 'Testsecond234',
                'last_name': 'Lastname',
                'email': 'test@email.com'
            }
        )

        self.assertEqual(200, response.status_code)

    def test_post_user_register_wrong_email(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.post(
            '/accounts/register/',
            {
                'username': 'testsecond',
                'password': '123456',
                'confirmPassword': '123456',
                'first_name': 'Testsecond',
                'last_name': 'Lastname',
                'email': 'testemail.com'
            }
        )

        self.assertEqual(200, response.status_code)

    def test_post_user_register_many_users(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.post(
            '/accounts/register/',
            {
                'username': 'testsecond',
                'password': '123456',
                'confirmPassword': '123456',
                'first_name': 'Testsecond',
                'last_name': 'Lastname',
                'email': 'admin@admin.com'
            }
        )

        self.assertEqual(200, response.status_code)

    def test_post_user_edit(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.post(
            '/accounts/edit_user/1/',
            {
                'username': 'testsecond',
                'password': '123456',
                'confirmPassword': '123456',
                'first_name': 'Testsecond',
                'last_name': 'Lastname',
                'email': 'test@email.com'
            }
        )

        self.assertEqual(200, response.status_code)

    def test_getting_user_edit(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get( '/accounts/edit_user/1/')

        self.assertEqual(200, response.status_code)

    def test_post_user_edit_wrong_pass_confirm(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.post(
            '/accounts/edit_user/1/',
            {
                'username': 'testsecond',
                'password': '123456',
                'confirmPassword': '123457',
                'first_name': 'Testsecond',
                'last_name': 'Lastname',
                'email': 'test@email.com'
            }
        )

        self.assertEqual(200, response.status_code)

    def test_post_user_edit_wrong_pass(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.post(
            '/accounts/edit_user/1/',
            {
                'username': 'testsecond',
                'password': '12345',
                'confirmPassword': '12345',
                'first_name': 'Testsecond',
                'last_name': 'Lastname',
                'email': 'test@email.com'
            }
        )

        self.assertEqual(200, response.status_code)


    def test_post_user_edit_wrong_first_name(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.post(
            '/accounts/edit_user/1/',
            {
                'username': 'testsecond',
                'password': '123456',
                'confirmPassword': '123456',
                'first_name': 'Testsecond9',
                'last_name': 'Lastname',
                'email': 'test@email.com'
            }
        )

        self.assertEqual(200, response.status_code)

    def test_post_user_edit_wrong_last_name(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.post(
            '/accounts/edit_user/1/',
            {
                'username': 'testsecond',
                'password': '123456',
                'confirmPassword': '123456',
                'first_name': 'Testsecond',
                'last_name': 'Lastname9',
                'email': 'test@email.com'
            }
        )

        self.assertEqual(200, response.status_code)

    def test_getting_user_delete(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get( '/accounts/delete_user/1/')

        self.assertEqual(200, response.status_code)

    def test_getting_user_logout(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get( '/accounts/logout/')

        self.assertEqual(302, response.status_code)

    def test_getting_pdf(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get('/reports/open_pdf/')
        print(response.status_code)

        self.assertEqual(200, response.status_code)
