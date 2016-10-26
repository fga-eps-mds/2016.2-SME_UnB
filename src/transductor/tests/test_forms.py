from django.test import TestCase
from transductor.forms import EnergyForm
from transductor.models import TransductorModel


class EnergyTransductorForm(TestCase):
    def setUp(self):
        t_model = TransductorModel()
        t_model.name = "TR 4020"
        t_model.transport_protocol = "UDP"
        t_model.serial_protocol = "Mosbus RTU"
        t_model.measurements_type = "EnergyMeasurements"
        t_model.register_addresses = [[68, 0], [70, 1]]
        t_model.save()

        self.t_model = t_model

    def test_valid_form(self):
        data = {
            'serie_number': 1,
            'ip_address': "111.111.111.111",
            'description': "Test",
            'model': self.t_model.id
        }

        form = EnergyForm(data=data)

        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {
            'serie_number': u'',
            'ip_address': "1",
            'description': u'',
            'model': u''
        }

        form = EnergyForm(data=data)

        self.assertFalse(form.is_valid())
