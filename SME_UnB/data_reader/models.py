from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.utils import timezone
from math import sqrt
from transductor.models import EnergyTransductor
import socket
import struct
import sys
import thread


class Observer():
    _observers = []

    def __init__(self):
        self._observers.append(self)
        self._observables = {}

    def observe(self, event_name, callback):
        self._observables[event_name] = callback


class VoltageObserver(Observer):
    def __init__(self):
        Observer.__init__(self)

    def verify_voltage(self, voltage):
        high_voltage = False

        if voltage > 230.0:
            high_voltage = True

        return high_voltage


class Event():
    def __init__(self, name, data, autofire=True):
        self.name = name
        self.data = data
        if autofire:
            self.fire()

    def fire(self):
        for observer in Observer._observers:
            if self.name in observer._observables:
                observer._observables[self.name](self.data)


class SerialProtocol(object):
    __metaclass__ = ABCMeta

    def __init__(self, transductor, port):
        self.transductor = transductor
        self.port = port

    @abstractmethod
    def create_messages(self):
        pass

    @abstractmethod
    def get_int_value_from_response(self, message_received_data):
        pass

    @abstractmethod
    def get_float_value_from_response(self, message_received_data):
        pass


class ModbusRTU(SerialProtocol):
    def __init__(self, transductor, port=1001):
        super(ModbusRTU, self).__init__(transductor, port)

    def create_messages(self):
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
                # TODO: add exception
                pass

            crc = struct.pack("<H", self._computate_crc(packaged_message))

            packaged_message = packaged_message + crc

            messages_to_send.append(packaged_message)

        return messages_to_send

    def get_int_value_from_response(self,  message_received_data):
        pass

    def get_float_value_from_response(self, message_received_data):
        n_bytes = struct.unpack("1B", message_received_data[2])[0]

        msg = bytearray(message_received_data[3:-2])

        for i in range(0, n_bytes, 4):
            if sys.byteorder == "little":
                msb = msg[i]
                msg[i] = msg[i+1]
                msg[i+1] = msb

                msb = msg[i+2]
                msg[i+2] = msg[i+3]
                msg[i+3] = msb
            else:
                msb = msg[i]
                lsb = msg[i+1]
                msg[i] = msg[i+2]
                msg[i+1] = msg[i+3]
                msg[i+2] = msb
                msg[i+3] = lsb

        value = struct.unpack("1f", msg)[0]
        return value

    def _computate_crc(self, packaged_message):
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
        return (self._computate_crc(packaged_message) == 0)

class CommunicationProtocol(models.Model):
    transductor = models.ForeignKey(EnergyTransductor)
    protocol_type = models.CharField(max_length=50)
    port = models.IntegerField(default=1001)
    timeout = models.FloatField(default=30.0)

    def __str__(self):
        return self.protocol_type

    def start_data_collection(self):
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        messages_to_send = []

        total_registers = 2
        initial_register = 68
        last_register = 93

        while(initial_register < last_register):
            if(initial_register == 86):
                initial_register = initial_register + 2
            else:
                packaged_message = struct.pack("2B", 0x01, 0x03) + struct.pack(
                    ">2H", initial_register, total_registers)

                crc = self._computate_crc(packaged_message)

                packaged_message = packaged_message + crc

                messages_to_send.append(packaged_message)

                initial_register = initial_register + 2

        alarm = VoltageObserver()

        try:
            thread.start_new_thread(self._thread_data_collection, (new_socket, messages_to_send, alarm))
        except:
            print "Can't create thread"

        return True

    def _thread_data_collection(self, socket, messages_to_send, alarm):
        messages = []

        for i in range(len(messages_to_send)):
            socket.sendto(messages_to_send[i], (self.transductor.ip_address, self.port))
            message_received = socket.recvfrom(256)

            messages.append(message_received[0])
            # alarm.observe('new data received', alarm.verify_voltage)
            # Event('new data received', value)

        collection_time = timezone.now()
        self._create_measurements_from_data_collected(messages, collection_time)

    def _create_measurements_from_data_collected(self, messages, collection_time):
        data = Measurements()

        data.transductor = self.transductor

        data.voltage_a = self._get_float_value_from_response(messages[0])
        data.voltage_b = self._get_float_value_from_response(messages[1])
        data.voltage_c = self._get_float_value_from_response(messages[2])

        data.current_a = self._get_float_value_from_response(messages[3])
        data.current_b = self._get_float_value_from_response(messages[4])
        data.current_c = self._get_float_value_from_response(messages[5])

        data.active_power_a = self._get_float_value_from_response(messages[6])
        data.active_power_b = self._get_float_value_from_response(messages[7])
        data.active_power_c = self._get_float_value_from_response(messages[8])

        data.reactive_power_a = self._get_float_value_from_response(messages[9])
        data.reactive_power_b = self._get_float_value_from_response(messages[10])
        data.reactive_power_c = self._get_float_value_from_response(messages[11])

        data.apparent_power_a = sqrt(data.active_power_a**2 + data.reactive_power_a**2)
        data.apparent_power_b = sqrt(data.active_power_b**2 + data.reactive_power_b**2)
        data.apparent_power_c = sqrt(data.active_power_c**2 + data.reactive_power_c**2)

        data.collection_date = collection_time

        data.save()

    def _get_float_value_from_response(self, message_received_data):
        n_bytes = struct.unpack("1B", message_received_data[2])[0]

        msg = bytearray(message_received_data[3:-2])

        for i in range(0, n_bytes, 4):
            if sys.byteorder == "little":
                msb = msg[i]
                msg[i] = msg[i+1]
                msg[i+1] = msb

                msb = msg[i+2]
                msg[i+2] = msg[i+3]
                msg[i+3] = msb
            else:
                msb = msg[i]
                lsb = msg[i+1]
                msg[i] = msg[i+2]
                msg[i+1] = msg[i+3]
                msg[i+2] = msb
                msg[i+3] = lsb

        value = struct.unpack("1f", msg)[0]
        return value
# @receiver(post_save, sender=EnergyTransductor)
# def transductor_saved(sender, instance, **kwargs):
#     instance.communicationprotocol_set.first().start_data_collection()
