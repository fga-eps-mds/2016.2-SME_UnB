from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
from transductor.models import EnergyTransductor, TransductorModel


class EnergyTransductorViewsTestCase(TestCase):
    def setUp(self):
        t_model = TransductorModel()
        t_model.name = "TR 4020"
        t_model.internet_protocol = "UDP"
        t_model.serial_protocol = "Modbus RTU"
        t_model.register_addresses = [68, 70, 72, 74, 76, 78, 80, 82, 84, 88, 90, 92]
        t_model.save()

    def test_index_access_and_template(self):
        url = reverse('transductor:index')
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'transductor/index.html')

    def test_index_without_transductor(self):
        url = reverse('transductor:index')
        response = self.client.get(url)

        self.assertIn("No Registered Transducer", response.content)

    def test_index_with_transductor(self):
        t_model = TransductorModel.objects.get(name="TR 4020")

        transductor = EnergyTransductor()
        transductor.serie_number = "1"
        transductor.description = "Test"
        transductor.creation_date = timezone.now()
        transductor.model = t_model
        transductor.ip_address = "111.111.111.111"
        transductor.save()

        url = reverse('transductor:index')
        response = self.client.get(url)

        self.assertIn(transductor.description, response.content)

    def test_not_create_energy_transductor_without_params(self):
        url = reverse('transductor:new')
        params = {
            'serie_number': u''
        }

        response = self.client.post(url, params)

        self.assertFormError(response, 'form', 'serie_number', 'This field is required.')
        self.assertFormError(response, 'form', 'ip_address', 'This field is required.')
        self.assertFormError(response, 'form', 'description', 'This field is required.')
        self.assertFormError(response, 'form', 'transductor_model', 'This field is required.')

    def test_create_valid_energy_transductor(self):
        t_model = TransductorModel.objects.get(name="TR 4020")
        transductor_count = EnergyTransductor.objects.count()

        url = reverse('transductor:new')

        params = {
            'serie_number': 1,
            'ip_address': '111.111.111.111',
            'description': 'Test',
            'transductor_model': t_model.id
        }

        response = self.client.post(url, params)

        self.assertEqual(transductor_count + 1, EnergyTransductor.objects.count())

        t_id = EnergyTransductor.objects.get(ip_address='111.111.111.111').id

        detail_url = reverse('transductor:detail', kwargs={'transductor_id': t_id})

        self.assertRedirects(response, detail_url)

    def test_not_create_transductor_with_wrong_ip_address(self):
        t_model = TransductorModel.objects.get(name="TR 4020")

        url = reverse('transductor:new')

        params = {
            'serie_number': 1,
            'ip_address': '1',
            'description': 'Test',
            'transductor_model': t_model.id
        }

        response = self.client.post(url, params)

        self.assertFormError(response, 'form', 'ip_address', 'Incorrect IP address format')

    def test_energy_transductor_detail(self):
        t_model = TransductorModel.objects.get(name="TR 4020")

        transductor = EnergyTransductor()
        transductor.serie_number = "1"
        transductor.description = "Test"
        transductor.creation_date = timezone.now()
        transductor.model = t_model
        transductor.ip_address = "111.111.111.111"
        transductor.save()

        url = reverse('transductor:detail', kwargs={'transductor_id': transductor.id})
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertIn("No measurement avaiable", response.content)
