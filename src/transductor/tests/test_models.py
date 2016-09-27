from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from transductor.models import EnergyTransductor, TransductorModel, EnergyOperations, EnergyMeasurements


class EnergyTransductorTestCase(TestCase):
    def setUp(self):
        t_model = TransductorModel()
        t_model.name = "TR 4020"
        t_model.internet_protocol = "UDP"
        t_model.serial_protocol = "Modbus RTU"
        t_model.register_addresses = [[68, 0], [70, 1]]
        t_model.save()

        self.t_model = t_model

        transductor = EnergyTransductor()
        transductor.serie_number = "1"
        transductor.description = "Test"
        transductor.creation_date = timezone.now()
        transductor.model = t_model
        transductor.ip_address = "111.111.111.111"
        transductor.save()

        self.transductor = transductor

    def test_should_not_create_transductor_with_wrong_ip_address(self):
        t_model = self.t_model

        transductor = EnergyTransductor()
        transductor.serie_number = "1"
        transductor.description = "Test"
        transductor.creation_date = timezone.now()
        transductor.model = t_model
        transductor.ip_address = "1"

        self.assertRaises(ValidationError, transductor.full_clean)

    def test_should_not_create_transductor_with_same_ip_address(self):
        t_model = self.t_model

        transductor = EnergyTransductor()
        transductor.serie_number = "2"
        transductor.description = "Test 2"
        transductor.creation_date = timezone.now()
        transductor.model = t_model
        transductor.ip_address = "111.111.111.111"

        self.assertRaises(IntegrityError, transductor.save)

    def test_str_from_transductor_model(self):
        t_model = self.t_model

        self.assertEqual(t_model.name, t_model.__str__())

    def test_str_from_energy_transductor(self):
        transductor = self.transductor

        self.assertEqual(transductor.description, transductor.__str__())

    def test_energy_operations(self):
        e_measurement = self.create_energy_measurement()

        colection_date = '%s' % e_measurement.collection_date

        self.assertEqual(colection_date, e_measurement.__str__())

        energy_operations = EnergyOperations(e_measurement)

        total_active_power = energy_operations.calculate_total_active_power()
        total_reactive_power = energy_operations.calculate_total_reactive_power()
        total_apparent_power = energy_operations.calculate_total_apparent_power()

        self.assertAlmostEqual(8.716, total_active_power, places=3, msg=None, delta=None)
        self.assertAlmostEqual(-2.254, total_reactive_power, places=3, msg=None, delta=None)
        self.assertAlmostEqual(9.059, total_apparent_power, places=3, msg=None, delta=None)

    def create_energy_measurement(self):
        time = timezone.now()

        e_measurement = EnergyMeasurements()
        e_measurement.transductor = self.transductor

        e_measurement.voltage_a = 122.875
        e_measurement.voltage_b = 122.784
        e_measurement.voltage_c = 121.611

        e_measurement.current_a = 22.831
        e_measurement.current_b = 17.187
        e_measurement.current_c = 3.950

        e_measurement.active_power_a = 2.794
        e_measurement.active_power_b = 1.972
        e_measurement.active_power_c = 3.950

        e_measurement.reactive_power_a = -0.251
        e_measurement.reactive_power_b = -0.752
        e_measurement.reactive_power_c = -1.251

        e_measurement.apparent_power_a = 2.805
        e_measurement.apparent_power_b = 2.110
        e_measurement.apparent_power_c = 4.144

        e_measurement.collection_date = time
        e_measurement.collection_minute = time.minute

        e_measurement.save()

        return e_measurement
