from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod
import socket
import struct
import sys


class SerialProtocol(object):
    """
        Base class for serial protocols.

        Attributes:
            - Transductor: The transductor which will hold communication.
    """
    __metaclass__ = ABCMeta

    def __init__(self, transductor):
        self.transductor = transductor

    @abstractmethod
    def create_messages(self):
        """
            Abstract method responsible to create messages following the header patterns
            of the serial protocol used.
        """
        pass

    @abstractmethod
    def get_int_value_from_response(self, message_received_data):
        """
            Abstract method responsible for read an integer value of a message sent by a transductor.

            :param message_received_data: The data from received message.
            :param type: str.
        """
        pass

    @abstractmethod
    def get_float_value_from_response(self, message_received_data):
        """
            Abstract method responsible for read an float value of a message sent by a transductor.

            :param message_received_data: The data from received message.
            :param type: str.
        """
        pass


class RegisterAddressException(Exception):
    def __init__(self, message):
        super(RegisterAddressException, self).__init__(message)
        self.message = message


class ModbusRTU(SerialProtocol):
    """
        Class responsible to represent the communication protocol Modbus in RTU mode.

        The RTU format follows the commands/data with a cyclic redundancy check checksum as an error
        check mechanism to ensure the reliability of data

        This protocol will be encapsulated in the data field of an transport protocol header.

        Click `here <http://modbus.org/docs/PI_MBUS_300.pdf>`_ to read the reference guide.
    """
    def __init__(self, transductor):
        super(ModbusRTU, self).__init__(transductor)

    def create_messages(self):
        """
            This method creates all messages based on transductor model register address
            that will be sent to a transductor seeking out their respective values.

            :returns: list -- The list with all messages.
        """
        registers = self.transductor.model.register_addresses

        messages_to_send = []

        int_addr = 0
        float_addr = 1

        address_value = 0
        address_type = 1

        for register in registers:
            if register[address_type] == int_addr:
                packaged_message = struct.pack("2B", 0x01, 0x03) + struct.pack(">2H", register[address_value], 1)
            elif register[address_type] == float_addr:
                packaged_message = struct.pack("2B", 0x01, 0x03) + struct.pack(">2H", register[address_value], 2)
            else:
                raise RegisterAddressException("Wrong register address type.")

            crc = struct.pack("<H", self._computate_crc(packaged_message))

            packaged_message = packaged_message + crc

            messages_to_send.append(packaged_message)

        return messages_to_send

    def get_int_value_from_response(self, message_received_data):
        """
            `Source Code <http://www.ccontrolsys.com/w/How_to_read_WattNode_Float_Registers_in_the_Python_Language>`_

            :param message_received_data: The data from received message.
            :param type: str.
            :returns: int -- The value from response.
        """
        n_bytes = struct.unpack("1B", message_received_data[2])[0]

        msg = bytearray(message_received_data[3:-2])

        for i in range(0, n_bytes, 2):
            if sys.byteorder == "little":
                msb = msg[i]
                msg[i] = msg[i + 1]
                msg[i + 1] = msb

        value = struct.unpack("1h", msg)[0]
        return value

    def get_float_value_from_response(self, message_received_data):
        """
            `Source Code <http://www.ccontrolsys.com/w/How_to_read_WattNode_Float_Registers_in_the_Python_Language>`_

            :param message_received_data: The data from received message.
            :param type: str.
            :returns: float -- the value from response.
        """
        n_bytes = struct.unpack("1B", message_received_data[2])[0]

        msg = bytearray(message_received_data[3:-2])

        for i in range(0, n_bytes, 4):
            if sys.byteorder == "little":
                msb = msg[i]
                msg[i] = msg[i + 1]
                msg[i + 1] = msb

                msb = msg[i + 2]
                msg[i + 2] = msg[i + 3]
                msg[i + 3] = msb
            else:
                msb = msg[i]
                lsb = msg[i + 1]
                msg[i] = msg[i + 2]
                msg[i + 1] = msg[i + 3]
                msg[i + 2] = msb
                msg[i + 3] = lsb

        value = struct.unpack("1f", msg)[0]
        return value

    def _computate_crc(self, packaged_message):
        """
            Method responsible to computate the crc from a packaged message.

            A cyclic redundancy check (CRC) is an error-detecting code commonly
            used in digital networks and storage devices to detect accidental changes to raw data.

            Click `here: <http://www.modbustools.com/modbus.html#crc>`_ to read Modbus CRC documentation.

            `Code Source <http://pythonhosted.org/pyModbusTCP/_modules/pyModbusTCP/client.html>`_

            :param packaged_message: The packaged message ready to be sent/received.
            :param type: str.
            :returns: int -- The CRC itself.
        """
        crc = 0xFFFF

        for index, item in enumerate(bytearray(packaged_message)):
            next_byte = item
            crc ^= next_byte
            for i in range(8):
                lsb = crc & 1
                crc >>= 1
                if lsb:
                    crc ^= 0xA001

        return crc

    def _check_crc(self, packaged_message):
        """
            Method responsible to verify if a CRC is valid.

            :param packaged_message: The packaged message ready to be sent/received.
            :param type: str.
            :returns: bool
        """
        return (self._computate_crc(packaged_message) == 0)

class TransportProtocol(object):
    """
        Base class for transport protocols.

        Attributes:
            - serial_protocol: The serial protocol used in communication.
            - transductor: The transductor which will hold communication.
            - timeout: The serial port used by the transductor.
            - port: The port used to communication.
    """
    __metaclass__ = ABCMeta

    def __init__(self, serial_protocol, timeout, port):
        self.serial_protocol = serial_protocol
        self.transductor = serial_protocol.transductor
        self.timeout = timeout
        self.port = port
        self.socket = None

    @abstractmethod
    def create_socket(self):
        """
            Abstract method responsible to create the respective transport socket.
        """
        pass


class UdpProtocol(TransportProtocol):
    def __init__(self, serial_protocol, timeout=10.0, port=1001):
        super(UdpProtocol, self).__init__(serial_protocol, timeout, port)

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.timeout)

    def send_messages(self):
        messages_to_send = self.serial_protocol.create_messages()

        messages = []

        for i in range(len(messages_to_send)):
            try:
                self.socket.sendto(messages_to_send[i], (self.transductor.ip_address, self.port))
                message_received = self.socket.recvfrom(256)
            except socket.timeout:
                print "timeout"
            except socket.error:
                print "error"

            messages.append(message_received[0])

        return messages
