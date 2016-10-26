from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod
from transductor.models import Transductor
import socket
import struct
import sys
import threading
import importlib


class SerialProtocol(object):
    """
    Base class for serial protocols.

    Attributes:
        transductor (Transductor): The transductor which will hold communication.
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
    def get_measurement_value_from_response(self, message_received_data):
        """
        Abstract method responsible for read an value of a message sent by transductor.

        Args:
            message_received_data (str): The data from received message.
        """
        pass


class RegisterAddressException(Exception):
    """
    Exception to signal that a register address from transductor model
    is in a wrong format.

    Attributes:
        message (str): The exception message.
    """
    def __init__(self, message):
        super(RegisterAddressException, self).__init__(message)
        self.message = message


class ModbusRTU(SerialProtocol):
    """
    Class responsible to represent the communication protocol Modbus in RTU mode.

    The RTU format follows the commands/data with a cyclic redundancy check checksum as an error
    check mechanism to ensure the reliability of data

    This protocol will be encapsulated in the data field of an transport protocol header.

    `Modbus reference guide <http://modbus.org/docs/PI_MBUS_300.pdf>`_
    """
    def __init__(self, transductor):
        super(ModbusRTU, self).__init__(transductor)

    def create_messages(self):
        """
        This method creates all messages based on transductor model register address
        that will be sent to a transductor seeking out their respective values.

        Returns:
            list: The list with all messages.

        Raises:
            RegisterAddressException: raised if the register address from transductor model
            is in a wrong format.
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

    def get_measurement_value_from_response(self, message_received_data):
        """
        Method responsible to read a value (int/float) from a Modbus RTU response.

        Args:
            message_received_data: The Modbus RTU response.

        Returns:
            int: if the value on response is an int.
            float: if the value on response is an float.
        """
        n_bytes = struct.unpack("1B", message_received_data[2])[0]

        msg = bytearray(message_received_data[3:-2])

        if n_bytes == 2:
            return self._unpack_int_response(n_bytes, msg)
        else:
            return self._unpack_float_response(n_bytes, msg)

    def _unpack_int_response(self, n_bytes, msg):
        """
        `Source Code <http://www.ccontrolsys.com/w/How_to_read_WattNode_Float_Registers_in_the_Python_Language>`_

        Args:
            message_received_data (str): The data from received message.

        Returns:
            int: The value from response.
        """
        for i in range(0, n_bytes, 2):
            if sys.byteorder == "little":
                msb = msg[i]
                msg[i] = msg[i + 1]
                msg[i + 1] = msb

        value = struct.unpack("1h", msg)[0]
        return value

    def _unpack_float_response(self, n_bytes, msg):
        """
        `Source Code <http://www.ccontrolsys.com/w/How_to_read_WattNode_Float_Registers_in_the_Python_Language>`_

        Args:
            message_received_data (str): The data from received message.

        Returns:
            float: The value from response.
        """
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

        `Modbus CRC documentation: <http://www.modbustools.com/modbus.html#crc>`_

        `Code Source <http://pythonhosted.org/pyModbusTCP/_modules/pyModbusTCP/client.html>`_

        Args:
            packaged_message (str): The packaged message ready to be sent/received.

        Returns:
            int: The CRC generated.
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

        Args:
            packaged_message (str): The packaged message ready to be sent/received.

        Returns:
            bool: True if CRC is valid, False otherwise.
        """
        return (self._computate_crc(packaged_message) == 0)

class BrokenTransductorException(Exception):
    """
    Exception to signal that a transductor is broken when trying to send messages
    via Transport Protocol.

    Attributes:
        message (str): The exception message.
    """
    def __init__(self, message):
        super(BrokenTransductorException, self).__init__(message)
        self.message = message

class TransportProtocol(object):
    """
    Base class for transport protocols.

    Attributes:
        serial_protocol (SerialProtocol): The serial protocol used in communication.
        transductor (Transductor): The transductor which will hold communication.
        timeout (float): The serial port used by the transductor.
        port (int): The port used to communication.
        socket (socket._socketobject): The socket used in communication.
    """
    __metaclass__ = ABCMeta

    def __init__(self, serial_protocol, timeout, port):
        self.serial_protocol = serial_protocol
        self.transductor = serial_protocol.transductor
        self.timeout = timeout
        self.port = port
        self.socket = None

    @abstractmethod
    def start_communication(self):
        """
        Abstract method responsible to start the communication with the transductor based
        on his transport protocol.
        """
        pass


class UdpProtocol(TransportProtocol):
    """
    Class responsible to represent a UDP protocol and handle all the communication.

    Attributes:
        receive_attemps (int): Total attempts to receive a message via socket UDP.
        max_receive_attempts (int): Maximum number of attemps to receive message via socket UDP.
    """
    def __init__(self, serial_protocol, timeout=0.5, port=1001):
        super(UdpProtocol, self).__init__(serial_protocol, timeout, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.receive_attempts = 0
        self.max_receive_attempts = 3

    def start_communication(self):
        """
        Method responsible to try receive message from transductor (via socket) based on maximum receive attempts.

        Everytime a message is not received from the socket the total of received attemps is increased.

        Returns: The messages received if successful, None otherwise.

        Raises:
            BrokenTransductorException: raised if the transductor can't send messages via
            UDP socket.
        """
        self.reset_receive_attempts()

        messages_to_send = self.serial_protocol.create_messages()
        received_messages = []

        while not received_messages and self.receive_attempts < self.max_receive_attempts:
            received_messages = self.handle_messages_via_socket(messages_to_send)

            if not received_messages:
                self.receive_attempts += 1

        if self.receive_attempts == self.max_receive_attempts:
            raise BrokenTransductorException("Transductor is broken!")

        return received_messages

    def reset_receive_attempts(self):
        """
        Method responsible to reset the number of receive attempts.
        """
        self.receive_attempts = 0

    def handle_messages_via_socket(self, messages_to_send):
        """
        Method responsible to handle send/receive messages via socket UDP.

        Args:
            messages_to_send (list): The requests to be sent to the transductor via socket.

        Returns:
            The messages received if successful, None otherwise.
        """
        messages = []

        for i, message in enumerate(messages_to_send):
            try:
                self.socket.sendto(message, (self.transductor.ip_address, self.port))
                message_received = self.socket.recvfrom(256)
            except socket.timeout:
                return None
            except socket.error:
                # TODO: add exception
                pass

            messages.append(message_received[0])

        return messages


class DataCollector(object):
    def __init__(self):
        self.transductors = Transductor.objects.all()
        self.transductor_module = importlib.import_module("transductor.models")

    def collect_data_thread(self, transductor):
        # Creating instances of the serial and transport protocol used by the transductor
        serial_protocol_instance = globals()[transductor.model.serial_protocol](transductor)
        tranport_protocol_instance = globals()[transductor.model.transport_protocol](serial_protocol_instance)

        try:
            messages = tranport_protocol_instance.start_communication()
        except BrokenTransductorException:
            if not transductor.broken:
                transductor.set_transductor_broken(True)
            return None

        if transductor.broken:
            transductor.set_transductor_broken(False)

        measurements = []

        for message in messages:
            measurements.append(serial_protocol_instance.get_measurement_value_from_response(message))

        GenericMeasurementsClass = getattr(self.transductor_module, transductor.model.measurements_type)
        generic_measurements_instance = GenericMeasurementsClass(transductor=transductor)
        generic_measurements_instance.save_measurements(measurements)

    def perform_all_data_collection(self):
        for transductor in self.transductors:
            collection_thread = threading.Thread(target=self.collect_data_thread, args=(transductor,))
            collection_thread.start()
