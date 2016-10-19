from django.test import TestCase
from data_reader.models import ModbusRTU, UdpProtocol, BrokenTransductorException
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
        # Starting UDP Handler
        HOST, PORT = "localhost", 9999
        self.server = SocketServer.UDPServer((HOST, PORT), UDPHandler)

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()

        # Creating Transductor Model and Energy Transductor
        t_model = TransductorModel()
        t_model.name = "TR 4020"
        t_model.internet_protocol = "UDP"
        t_model.serial_protocol = "Modbus RTU"
        t_model.register_addresses = [[4, 0], [68, 1]]
        t_model.save()

        self.t_model = t_model

        transductor = EnergyTransductor()
        transductor.serie_number = "1"
        transductor.description = "Test"
        transductor.model = t_model
        transductor.ip_address = HOST
        transductor.save()

        self.transductor = transductor

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_create_socket(self):
        modbus_rtu = ModbusRTU(self.transductor)
        udp_protocol = UdpProtocol(serial_protocol=modbus_rtu, timeout=0.5)

        udp_protocol.create_socket()

        self.assertEqual(socket.AF_INET, udp_protocol.socket.family)
        self.assertEqual(socket.SOCK_DGRAM, udp_protocol.socket.type)
        self.assertEqual(0.5, udp_protocol.socket.gettimeout())

    def test_reset_receive_attempts(self):
        modbus_rtu = ModbusRTU(self.transductor)
        udp_protocol = UdpProtocol(serial_protocol=modbus_rtu, timeout=0.5, port=9999)

        udp_protocol.receive_attempts += 1

        self.assertEqual(1, udp_protocol.receive_attempts)

        udp_protocol.reset_receive_attempts()

        self.assertEqual(0, udp_protocol.receive_attempts)

    def test_receive_message_via_socket_udp(self):
        modbus_rtu = ModbusRTU(self.transductor)
        udp_protocol = UdpProtocol(serial_protocol=modbus_rtu, timeout=0.5, port=9999)
        udp_protocol.create_socket()

        messages_to_send = [
            'Request 1',
            'Request 2'
        ]

        messages = udp_protocol.handle_messages_via_socket(messages_to_send)

        response = [
            'Response 1',
            'Response 2'
        ]

        self.assertEqual(response, messages)

    def test_udp_socket_timeout(self):
        wrong_ip_address = '0.0.0.0'
        self.transductor.ip_address = wrong_ip_address

        modbus_rtu = ModbusRTU(self.transductor)
        udp_protocol = UdpProtocol(serial_protocol=modbus_rtu, timeout=0.5)
        udp_protocol.create_socket()

        messages_to_send = [
            'Request 1',
            'Request 2'
        ]

        messages = udp_protocol.handle_messages_via_socket(messages_to_send)

        self.assertIsNone(messages)

    @mock.patch.object(UdpProtocol, 'handle_messages_via_socket', return_value=None, autospec=True)
    def test_manage_received_messages_with_transductor_not_broken_and_socket_timeout(self, mock_method):
        modbus_rtu = ModbusRTU(self.transductor)
        udp_protocol = UdpProtocol(serial_protocol=modbus_rtu, timeout=0.5)

        messages = 'any messages'

        with self.assertRaises(BrokenTransductorException):
            udp_protocol.manage_received_messages(messages)

        self.assertEqual(udp_protocol.receive_attempts, udp_protocol.max_receive_attempts)

    @mock.patch.object(UdpProtocol, 'handle_messages_via_socket', return_value='any return', autospec=True)
    def test_manage_received_messages_working_properly(self, mock_method):
        modbus_rtu = ModbusRTU(self.transductor)
        udp_protocol = UdpProtocol(serial_protocol=modbus_rtu, timeout=0.5)

        messages = 'any messages'

        self.assertEqual('any return', udp_protocol.manage_received_messages(messages))
        self.assertEqual(0, udp_protocol.receive_attempts)
