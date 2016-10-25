from django.test import TestCase
from django.utils import timezone
from transductor.models import TransductorModel, EnergyTransductor
from data_reader.models import ModbusRTU, SerialProtocol, RegisterAddressException
import mock


class ModBusRTUTestCase(TestCase):
    def setUp(self):
        t_model = TransductorModel()
        t_model.name = "TR 4020"
        t_model.transport_protocol = "UDP"
        t_model.serial_protocol = "Modbus RTU"
        t_model.register_addresses = [[4, 0], [68, 1]]
        t_model.save()

        self.t_model = t_model

        transductor = EnergyTransductor()
        transductor.serie_number = "1"
        transductor.description = "Test"
        transductor.model = t_model
        transductor.ip_address = "111.111.111.111"
        transductor.save()

        self.transductor = transductor

        self.modbus_rtu = ModbusRTU(self.transductor)

    def test_create_messages(self):
        messages = self.modbus_rtu.create_messages()

        int_message = messages[0]

        float_message = messages[1]

        self.assertEqual('\x01\x03\x00\x04\x00\x01\xc5\xcb', int_message)
        self.assertEqual('\x01\x03\x00D\x00\x02\x84\x1e', float_message)

    def test_read_int_value_from_response(self):
        response = '\x01\x03\x02\x00\xdc\xb9\xdd'

        int_value = self.modbus_rtu.get_measurement_value_from_response(response)

        self.assertEqual(int_value, 220)

    def test_read_float_value_from_response(self):
        response_1 = '\x01\x03\x04_pC\\\xd8\xf5'
        response_2 = '\x01\x03\x04dIC\\\x05\xdc'
        response_3 = '\x01\x03\x04\xa3BCY\x89i'

        float_value_1 = self.modbus_rtu.get_measurement_value_from_response(response_1)
        float_value_2 = self.modbus_rtu.get_measurement_value_from_response(response_2)
        float_value_3 = self.modbus_rtu.get_measurement_value_from_response(response_3)

        self.assertAlmostEqual(float_value_1, 220.372802734375, places=7, msg=None, delta=None)
        self.assertAlmostEqual(float_value_2, 220.39173889160156, places=7, msg=None, delta=None)
        self.assertAlmostEqual(float_value_3, 217.63772583007812, places=7, msg=None, delta=None)

    def test_check_crc_right_response(self):
        response_1 = '\x01\x03\x04\x16@D\xa6L\xd5'
        response_2 = '\x01\x03\x04\x10OC\xb9?\xa6'
        response_3 = '\x01\x03\x04jUD\xe1\x04\xb3'

        self.assertEqual(True, self.modbus_rtu._check_crc(response_1))
        self.assertEqual(True, self.modbus_rtu._check_crc(response_2))
        self.assertEqual(True, self.modbus_rtu._check_crc(response_3))

    def test_check_crc_wrong_response(self):
        response_1 = '\x01\x03\x04\x16@D\xa6L\xd4'
        response_2 = '\x01\x03\x04\x10OC\xb9?\xa5'
        response_3 = '\x01\x03\x04jUD\xe1\x04\xb2'

        self.assertEqual(False, self.modbus_rtu._check_crc(response_1))
        self.assertEqual(False, self.modbus_rtu._check_crc(response_2))
        self.assertEqual(False, self.modbus_rtu._check_crc(response_3))

    def test_abstract_methods_from_serial_protocol(self):
        self.assertEqual(None, SerialProtocol.create_messages(self.modbus_rtu))

    def test_raise_exception_on_create_messages_with_wrong_address(self):
        wrong_address = [[4, 2]]

        t_model = TransductorModel()
        t_model.name = "Test Model"
        t_model.transport_protocol = "UDP"
        t_model.serial_protocol = "Modbus RTU"
        t_model.register_addresses = wrong_address
        t_model.save()

        transductor = EnergyTransductor()
        transductor.serie_number = "2"
        transductor.description = "Test 2"
        transductor.creation_date = timezone.now()
        transductor.model = t_model
        transductor.ip_address = "222.222.222.222"
        transductor.save()

        modbus = ModbusRTU(transductor)

        with self.assertRaises(RegisterAddressException):
            modbus.create_messages()

    @mock.patch.object(ModbusRTU, '_unpack_int_response', return_value=1, autospec=True)
    @mock.patch.object(ModbusRTU, '_unpack_float_response', return_value=5.0, autospec=True)
    def test_modbusrtu_get_measurement_value_from_response(self, float_mock_method, int_mock_method):
        int_response = '\x01\x03\x02\x00\xdc\xb9\xdd'
        float_response = '\x01\x03\x04_pC\\\xd8\xf5'

        int_value = self.modbus_rtu.get_measurement_value_from_response(int_response)
        self.assertEqual(1, int_value)

        float_value = self.modbus_rtu.get_measurement_value_from_response(float_response)
        self.assertEqual(5.0, float_value)
