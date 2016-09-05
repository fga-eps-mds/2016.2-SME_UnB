from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from transductor.models import EnergyTransductor, TransductorModel


class EnergyTransductorTestCase(TestCase):
    def setUp(self):
        t_model = TransductorModel()
        t_model.name = "TR 4020"
        t_model.internet_protocol = "UDP"
        t_model.serial_protocol = "Modbus RTU"
        t_model.register_addresses = [68, 70, 72, 74, 76, 78, 80, 82, 84, 88, 90, 92]
        t_model.save()

        transductor = EnergyTransductor()
        transductor.serie_number = "1"
        transductor.description = "Test"
        transductor.creation_date = timezone.now()
        transductor.model = t_model
        transductor.ip_address = "111.111.111.111"
        transductor.save()

    def test_should_not_create_transductor_with_wrong_ip_address(self):
        t_model = TransductorModel.objects.get(name="TR 4020")

        transductor = EnergyTransductor()
        transductor.serie_number = "1"
        transductor.description = "Test"
        transductor.creation_date = timezone.now()
        transductor.model = t_model
        transductor.ip_address = "1"

        self.assertRaises(ValidationError, transductor.full_clean)

    def test_should_not_create_transductor_with_same_ip_address(self):
        t_model = TransductorModel.objects.get(name="TR 4020")

        transductor = EnergyTransductor()
        transductor.serie_number = "2"
        transductor.description = "Test 2"
        transductor.creation_date = timezone.now()
        transductor.model = t_model
        transductor.ip_address = "111.111.111.111"

        self.assertRaises(IntegrityError, transductor.save)

    def test_str_from_transductor_model(self):
        t_model = TransductorModel.objects.get(name="TR 4020")

        self.assertEqual(t_model.name, t_model.__str__())

    def test_str_from_energy_transductor(self):
        transductor = EnergyTransductor.objects.get(ip_address="111.111.111.111")

        self.assertEqual(transductor.description, transductor.__str__())
