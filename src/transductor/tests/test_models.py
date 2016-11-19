from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from transductor.models import EnergyTransductor, TransductorModel, EnergyOperations, EnergyMeasurements, Measurements
import numpy


class EnergyTransductorTestCase(TestCase):
    def setUp(self):
        t_model = TransductorModel()
        t_model.name = "TR 4020"
        t_model.transport_protocol = "UDP"
        t_model.serial_protocol = "Modbus RTU"
        t_model.register_addresses = [[68, 0], [70, 1]]
        t_model.save()

        self.t_model = t_model

        transductor = EnergyTransductor()
        transductor.serie_number = "1"
        transductor.description = "Test"
        transductor.model = t_model
        transductor.ip_address = "111.111.111.111"
        transductor.save()

        self.transductor = transductor

        self.create_energy_measurements()

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

    def test_calculate_total_power_and_str_method(self):
        e_measurement = EnergyMeasurements.objects.get(voltage_a=122.875, voltage_b=122.784, voltage_c=121.611)

        colection_date = '%s' % e_measurement.collection_date

        self.assertEqual(colection_date, e_measurement.__str__())

        total_active_power = EnergyOperations.calculate_total_power(e_measurement.active_power_a, e_measurement.active_power_b, e_measurement.active_power_c)

        self.assertAlmostEqual(8.716, total_active_power, places=3, msg=None, delta=None)

    def test_calculate_apparent_power(self):
        self.assertEqual(5, EnergyOperations.calculate_apparent_power(3, 4))
        self.assertEqual(13, EnergyOperations.calculate_apparent_power(12, 5))
        self.assertEqual(25, EnergyOperations.calculate_apparent_power(24, 7))

    def test_annual_energy_measurements(self):
        data = EnergyMeasurements.mng_objects.average_annual(2016, 'voltage_a', 'voltage_b', 'voltage_c')

        average_result = numpy.array([124.375, 124.284, 123.111])

        self.assertTrue((data == average_result).all())

    def test_set_transductor_broken(self):
        self.transductor.set_transductor_broken(True)
        self.assertTrue(self.transductor.broken)

        self.transductor.set_transductor_broken(False)
        self.assertFalse(self.transductor.broken)

    def test_father_method_save_measurements(self):
        measurements = Measurements()
        self.assertEqual(None, measurements.save_measurements('any value'))

    def create_energy_measurements(self):
        for index in range(0, 4):
            e_measurement = EnergyMeasurements()
            e_measurement.transductor = self.transductor

            e_measurement.voltage_a = 122.875 + index
            e_measurement.voltage_b = 122.784 + index
            e_measurement.voltage_c = 121.611 + index

            e_measurement.current_a = 22.831 + index
            e_measurement.current_b = 17.187 + index
            e_measurement.current_c = 3.950 + index

            e_measurement.active_power_a = 2.794 + index
            e_measurement.active_power_b = 1.972 + index
            e_measurement.active_power_c = 3.950 + index

            e_measurement.reactive_power_a = -0.251 - index
            e_measurement.reactive_power_b = -0.752 - index
            e_measurement.reactive_power_c = -1.251 - index

            e_measurement.apparent_power_a = 2.805 + index
            e_measurement.apparent_power_b = 2.110 + index
            e_measurement.apparent_power_c = 4.144 + index

            time = timezone.now()
            e_measurement.collection_minute = time.minute

            e_measurement.save()
