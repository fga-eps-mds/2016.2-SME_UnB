from django.test import Client

import unittest


class TestReportView(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_getting_page_report(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get('/reports/report/1/')

        self.assertEqual(302, response.status_code)

    def test_getting_wrong_page_report(self):
        response = self.client.post(
            '/reports/reports/',
            {"username": 'temporary', 'password': 'temporary'}
        )

        self.assertEqual(404, response.status_code)

    def test_getting_pdf(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get('/reports/open_pdf/')

        self.assertEqual(302, response.status_code)


    def test_getting_wrong_page_filter(self):
        response = self.client.post(
            '/reports/transductors_filt/',
            {"username": 'temporary', 'password': 'temporary'}
        )

        self.assertEqual(404, response.status_code)

    def test_getting_page_transductor_list(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get('/reports/transductor_list/')

        self.assertEqual(200, response.status_code)

    def test_getting_wrong_page_transductor_list(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get('/reports/transductores_list/')

        self.assertEqual(404, response.status_code)

    def test_getting_page_transductor_filter(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get('/reports/transductors_filter/')

        self.assertEqual(200, response.status_code)

    def test_getting_wrong_page_transductor_filter(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get('/reports/transductores_filter/')

        self.assertEqual(404, response.status_code)

    def test_getting_page_invoice(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get('/reports/invoice/')

        self.assertEqual(200, response.status_code)

    def test_getting_wrong_page_invoice(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get('/reports/invoice/')

        self.assertEqual(404, response.status_code)

    def test_getting_page_charts(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get('/reports/return_chart/')

        self.assertEqual(200, response.status_code)
