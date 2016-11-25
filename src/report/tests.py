from django.test import Client
from . import views
import unittest
import datetime
import os.path
from django.utils import timezone
from transductor.models import TransductorModel,EnergyTransductor,EnergyMeasurements

class TestReportView(unittest.TestCase):
    def setUp(self):
        self.client = Client()

        address =[[68, 0], [70, 1]]
        self.t_model = TransductorModel(name="Test Name",
                                   transport_protocol="UDP",
                                   serial_protocol="Modbus RTU",
                                   register_addresses= address)
        self.t_model.save()
        self.e_transductor = EnergyTransductor(model=self.t_model,
                                            serie_number=1,
                                            ip_address="1.1.1.1",
                                            description="Energy Transductor Test",
                                            creation_date=timezone.now())

        self.e_transductor.save()
        self.e_measurements = EnergyMeasurements(transductor=self.e_transductor,
                                               voltage_a=122.875,
                                               voltage_b=122.784,
                                               voltage_c=121.611,
                                               current_a=22.831,
                                               current_b=17.187,
                                               current_c= 3.950,
                                               active_power_a=2.794,
                                               active_power_b=1.972,
                                               active_power_c=3.950,
                                               reactive_power_a=-0.251,
                                               reactive_power_b=-0.752,
                                               reactive_power_c=-1.251,
                                               apparent_power_a=2.805,
                                               apparent_power_b=2.110,
                                               apparent_power_c=4.144,
                                               collection_minute=timezone.now().minute)
        self.e_measurements.save()
        # self.assertEqual(1, 2)

    def tearDown(self):

        self.t_model.delete()
        self.e_transductor.delete()
        #self.e_measurements.delete()


    def test_getting_page_report(self):
        logged_in = self.client.login(username='testuser', password='12345')
        response = self.client.get('/reports/report/' + str(self.e_transductor.id)+ '/')
        print'aqui'
        print(EnergyMeasurements.objects.all())

        self.assertEqual(200, response.status_code)

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
        response = self.client.get('/reports/invoice/'+ str(self.e_transductor.id))

        self.assertEqual(301, response.status_code)

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




