from django.test import TestCase
from django.utils import timezone
from transductor.models import TransductorModel, EnergyTransductor, EnergyMeasurements
from data_reader.models import ModbusRTU, SerialProtocol, RegisterAddressException, DataCollector, UdpProtocol, BrokenTransductorException
import mock
from threading import Thread


class ModBusRTUTestCase(TestCase):
    def setUp(self):
        t_model = TransductorModel()
        t_model.name = "TR 4020"
        t_model.transport_protocol = "UdpProtocol"
        t_model.serial_protocol = "ModbusRTU"
        t_model.register_addresses = [[4, 0], [68, 1]]
        t_model.measurements_type = "EnergyMeasurements"
        t_model.save()

        self.t_model = t_model

        transductor = EnergyTransductor()
        transductor.serie_number = "1"
        transductor.description = "Test"
        transductor.model = t_model
        transductor.ip_address = "111.111.111.111"
        transductor.broken = False
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
        self.assertEqual(None, SerialProtocol.get_measurement_value_from_response(self.modbus_rtu, 'any message'))

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

    @mock.patch.object(DataCollector, 'collect_data_thread', return_value='any return', autospec=True)
    @mock.patch.object(Thread, 'start', return_value=None)
    def test_data_collector_perform_all_data_collection(self, mock_start, mock_collect_data_thread):
        data_collector = DataCollector()
        data_collector.perform_all_data_collection()

        mock_start.assert_called_with()

    @mock.patch.object(UdpProtocol, 'start_communication', side_effect=BrokenTransductorException('Transductor is Broken!'))
    def test_collect_data_thread_with_transductor_broken_and_receive_timeout(self, mock_start_communication):
        self.transductor.broken = True

        data_collector = DataCollector()
        data_collector.collect_data_thread(self.transductor)

        mock_start_communication.assert_called_with()

    @mock.patch.object(EnergyTransductor, 'set_transductor_broken', return_value=None)
    @mock.patch.object(UdpProtocol, 'start_communication', side_effect=BrokenTransductorException('Transductor is Broken!'))
    def test_collect_data_thread_with_transductor_not_broken_and_receive_timeout(self, mock_1, mock_2):
        data_collector = DataCollector()
        data_collector.collect_data_thread(self.transductor)

        mock_1.assert_called_with()
        mock_2.assert_called_with(True)

    @mock.patch.object(EnergyMeasurements, 'save_measurements', return_value=None)
    @mock.patch.object(ModbusRTU, 'get_measurement_value_from_response', return_value=1)
    @mock.patch.object(EnergyTransductor, 'set_transductor_broken', return_value=None)
    @mock.patch.object(UdpProtocol, 'start_communication', return_value=['Message 1', 'Message 2'])
    def test_collect_data_thread_with_transductor_broken_and_not_receive_timeout(self, mock_1, mock_2, mock_3, mock_4):
        self.transductor.broken = True

        data_collector = DataCollector()
        data_collector.collect_data_thread(self.transductor)

        mock_1.assert_called_with()
        mock_2.assert_called_with(False)

        calls = [mock.call('Message 1'), mock.call('Message 2')]
        mock_3.assert_has_calls(calls)

        mock_4.assert_called_with([1, 1])

    @mock.patch.object(EnergyMeasurements, 'save_measurements', return_value=None)
    @mock.patch.object(ModbusRTU, 'get_measurement_value_from_response', return_value=1)
    @mock.patch.object(UdpProtocol, 'start_communication', return_value=['Message 1', 'Message 2'])
    def test_collect_data_thread_with_transductor_broken_and_not_timeout(self, mock_1, mock_2, mock_3):
        data_collector = DataCollector()
        data_collector.collect_data_thread(self.transductor)

        mock_1.assert_called_with()

        calls = [mock.call('Message 1'), mock.call('Message 2')]
        mock_2.assert_has_calls(calls)

        mock_3.assert_called_with([1, 1])
