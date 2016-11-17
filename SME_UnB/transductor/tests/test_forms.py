from django.test import TestCase
from transductor.forms import EnergyForm
from transductor.models import TransductorModel


class EnergyTransductorForm(TestCase):
    def setUp(self):
        t_model = TransductorModel()
        t_model.name = "TR 4020"
        t_model.internet_protocol = "UDP"
        t_model.serial_protocol = "Modbus RTU"
        t_model.register_addresses = [68, 70, 72, 74, 76, 78,
                                      80, 82, 84, 88, 90, 92]
        t_model.save()

    def test_valid_form(self):
        t_model = TransductorModel.objects.get(name="TR 4020")

        data = {
            'serie_number': 1,
            'ip_address': "111.111.111.111",
            'description': "Test",
            'transductor_model': t_model.id
        }

        form = EnergyForm(data=data)

        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        t_model = TransductorModel.objects.get(name="TR 4020")

        data = {
            'serie_number': u'',
            'ip_address': "1",
            'description': u'',
            'transductor_model': u''
        }

        form = EnergyForm(data=data)

        self.assertFalse(form.is_valid())
