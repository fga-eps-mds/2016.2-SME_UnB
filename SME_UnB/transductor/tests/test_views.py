from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
from transductor.models import EnergyTransductor, TransductorModel


class EnergyTransductorViewsTestCase(TestCase):
    def setUp(self):
        t_model = TransductorModel()
        t_model.name = "TR 4020"
        t_model.internet_protocol = "UDP"
        t_model.serial_protocol = "Mosbus RTU"
        t_model.register_addresses = [[68, 0], [70, 1]]
        t_model.save()

        self.t_model = t_model

        transductor = self.create_energy_transductor(1, "Test Transductor", "1.1.1.1", t_model)

        self.transductor = transductor

    def test_index_access_and_template(self):
        url = reverse('transductor:index')
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'transductor/index.html')

    def test_index_with_transductor(self):
        transductor = self.transductor

        url = reverse('transductor:index')

        response = self.client.get(url)

        self.assertIn(transductor.description, response.content)

    def test_transductor_creation_page(self):
        url = reverse('transductor:new')

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

    def test_not_create_energy_transductor_without_params(self):
        url = reverse('transductor:new')

        params = {
            'serie_number': u'',
            'ip_address': u'',
            'description': u'',
            'transductor_model': u''
        }

        response = self.client.post(url, params)

        self.assertFormError(response, 'form', 'serie_number', 'This field is required.')
        self.assertFormError(response, 'form', 'ip_address', 'This field is required.')
        self.assertFormError(response, 'form', 'description', 'This field is required.')
        self.assertFormError(response, 'form', 'transductor_model', 'This field is required.')

    def test_create_valid_energy_transductor(self):
        t_model = self.t_model
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

    def test_not_create_transductor_with_same_ip_address(self):
        t_model = self.t_model

        transductor = self.transductor

        url = reverse('transductor:new')

        params = {
            'serie_number': 1,
            'ip_address': transductor.ip_address,
            'description': 'Test',
            'transductor_model': t_model.id
        }

        response = self.client.post(url, params)

        self.assertFormError(response, 'form', 'ip_address', 'Energy transductor with this Ip address already exists.')

    def test_not_create_transductor_with_wrong_ip_address(self):
        t_model = self.t_model

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
        t_model = self.t_model

        transductor = self.create_energy_transductor(1, "Test", "111.111.111.111", t_model)

        url = reverse('transductor:detail', kwargs={'transductor_id': transductor.id})
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertIn("No measurement avaiable", response.content)

    def test_transductor_editing_page(self):
        transductor = self.transductor

        url = reverse('transductor:edit', kwargs={'transductor_id': transductor.id})

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

    def test_edit_transductor(self):
        t_model = self.t_model

        url = reverse('transductor:edit', kwargs={'transductor_id': self.transductor.id})

        params = {
            'serie_number': 2,
            'ip_address': '222.222.222.222',
            'description': 'Another Test',
            'transductor_model': t_model.id
        }

        self.client.post(url, params)

        transductor = EnergyTransductor.objects.get(ip_address='222.222.222.222')

        self.assertEqual(2, transductor.serie_number)
        self.assertEqual("Another Test", transductor.description)

    def test_not_edit_transductor_with_wrong_params(self):
        t_model = self.t_model

        url = reverse('transductor:edit', kwargs={'transductor_id': self.transductor.id})

        params = {
            'serie_number': 2,
            'ip_address': 'Wrong Ip Addres',
            'description': 'Another Test',
            'transductor_model': t_model.id
        }

        response = self.client.post(url, params)

        self.assertFormError(response, 'form', 'ip_address', 'Incorrect IP address format')

    def test_delete_energy_transductor(self):
        t_model = self.t_model

        transductor = self.create_energy_transductor(1, "Test", "111.111.111.111", t_model)

        transductor_count = EnergyTransductor.objects.count()

        url = reverse('transductor:delete', kwargs={'transductor_id': transductor.id})

        params = {
            'delete': u''
        }

        self.client.post(url, params)

        self.assertEqual(transductor_count - 1, EnergyTransductor.objects.count())

    def test_not_delete_energy_transductor_with_get_method(self):
        t_model = self.t_model

        transductor = self.create_energy_transductor(1, "Test", "111.111.111.111", t_model)

        transductor_count = EnergyTransductor.objects.count()

        url = reverse('transductor:delete', kwargs={'transductor_id': transductor.id})

        self.client.get(url)

        self.assertEqual(transductor_count, EnergyTransductor.objects.count())

    def create_energy_transductor(self, serie_number, description, ip_address, t_model):
        transductor = EnergyTransductor()
        transductor.serie_number = serie_number
        transductor.description = description
        transductor.creation_date = timezone.now()
        transductor.ip_address = ip_address
        transductor.model = t_model
        transductor.save()

        return transductor
