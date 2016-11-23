from django.test import Client
from . import views
import unittest
import datetime
import os.path

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
        response = self.client.get('/reports/open_pdf/1/')

        self.assertEqual(200, response.status_code)


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

    def test_create_graphic(self):
        now = datetime.datetime.now();
        delta = datetime.timedelta(days=1)

        a = datetime.datetime.today()
        numdays = 3
        dateList = []
        for x in range (0, numdays):
            dateList.append(a - datetime.timedelta(days = x))

        self.graphic = views.create_graphic(path='src/report/static/currentGraphic1.png',
                        array_date=[12,13,14],
                        array_dateb=[56,67,78],
                        array_datec=[34,45,56],
                        array_data=dateList,
                        label='Current')

        image = ("src/report/static/currentGraphic1.png")
        self.assertTrue(os.path.isfile(image))
        self.assertEqual(self.graphic,'src/report/static/currentGraphic1.png')

    def test_create_generatePdf(self):
       views.generatePdf('1')
       pdf = ("src/report/static/Relatorio1.pdf")
       self.assertTrue(os.path.isfile(pdf))




