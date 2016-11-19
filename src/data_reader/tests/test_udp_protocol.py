from django.test import TestCase
from data_reader.models import ModbusRTU, UdpProtocol, BrokenTransductorException, TransportProtocol
from transductor.models import EnergyTransductor, TransductorModel
import threading
import mock
import socket
import SocketServer


class UDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]

        if data == 'Request 1':
            response = 'Response 1'
            socket.sendto(response, self.client_address)
        elif data == 'Request 2':
            response = 'Response 2'
            socket.sendto(response, self.client_address)
        else:
            pass


class UDPProtocolTest(TestCase):
    def setUp(self):
        HOST, PORT = "localhost", 9999

        # Creating Transductor Model and Energy Transductor
        t_model = TransductorModel()
        t_model.name = "TR 4020"
        t_model.transport_protocol = "UDP"
        t_model.serial_protocol = "Modbus RTU"
        t_model.register_addresses = [[4, 0], [68, 1]]
        t_model.save()

        transductor = EnergyTransductor()
        transductor.serie_number = "1"
        transductor.description = "Test"
        transductor.model = t_model
        transductor.ip_address = HOST
        transductor.save()

        # Setting instance attributes
        self.t_model = t_model
        self.transductor = transductor
        self.modbus_rtu = ModbusRTU(self.transductor)
        self.udp_protocol = UdpProtocol(serial_protocol=self.modbus_rtu, timeout=0.5, port=9999)

        # Starting UDP server via thread
        self.server = SocketServer.UDPServer((HOST, PORT), UDPHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_create_socket(self):
        self.assertEqual(socket.AF_INET, self.udp_protocol.socket.family)
        self.assertEqual(socket.SOCK_DGRAM, self.udp_protocol.socket.type)
        self.assertEqual(0.5, self.udp_protocol.socket.gettimeout())

    def test_reset_receive_attempts(self):
        self.udp_protocol.receive_attempts += 1
        self.assertEqual(1, self.udp_protocol.receive_attempts)

        self.udp_protocol.reset_receive_attempts()
        self.assertEqual(0, self.udp_protocol.receive_attempts)

    def test_receive_message_via_socket_udp(self):
        messages_to_send = [
            'Request 1',
            'Request 2'
        ]

        messages = self.udp_protocol.handle_messages_via_socket(messages_to_send)

        response = [
            'Response 1',
            'Response 2'
        ]

        self.assertEqual(response, messages)

    def test_udp_socket_timeout(self):
        wrong_ip_address = '0.0.0.0'
        self.transductor.ip_address = wrong_ip_address

        test_modbus_rtu = ModbusRTU(self.transductor)
        test_udp_protocol = UdpProtocol(serial_protocol=test_modbus_rtu, timeout=0.5)

        messages_to_send = [
            'Request 1',
            'Request 2'
        ]

        messages = test_udp_protocol.handle_messages_via_socket(messages_to_send)

        self.assertIsNone(messages)

    @mock.patch.object(ModbusRTU, 'create_messages', return_value='any created messages', autospec=True)
    @mock.patch.object(UdpProtocol, 'handle_messages_via_socket', return_value=None, autospec=True)
    def test_start_communication_with_transductor_not_broken_and_socket_timeout(self, mock_udp_method, mock_modbus_method):
        with self.assertRaises(BrokenTransductorException):
            self.udp_protocol.start_communication()

        self.assertEqual(self.udp_protocol.receive_attempts, self.udp_protocol.max_receive_attempts)

    @mock.patch.object(ModbusRTU, 'create_messages', return_value='any created messages', autospec=True)
    @mock.patch.object(UdpProtocol, 'handle_messages_via_socket', return_value='any return', autospec=True)
    def test_start_communication_working_properly(self, mock_udp_method, mock_modbus_method):
        self.assertEqual('any return', self.udp_protocol.start_communication())
        self.assertEqual(0, self.udp_protocol.receive_attempts)

    def test_start_communication_abstract_method(self):
        self.assertEqual(None, TransportProtocol.start_communication(self.udp_protocol))
