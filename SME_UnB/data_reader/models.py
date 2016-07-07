from __future__ import unicode_literals
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.utils import timezone
import socket
import struct
import sys
import time
import thread


class TransductorManager(models.Model):
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.description


class Transductor(models.Model):
    transductor_manager = models.ForeignKey(TransductorManager)
    serie_number = models.IntegerField(default=None)
    ip_address = models.CharField(max_length=15)
    description = models.TextField(max_length=150)
    creation_date = models.DateTimeField('date published')
    data_collection = models.BooleanField(default=False)

    def __str__(self):
        return self.description


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
        low_voltage = False

        if voltage < 220.0:
            low_voltage = True

        return low_voltage


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


class CommunicationProtocol(models.Model):
    transductor = models.ForeignKey(Transductor)
    protocol_type = models.CharField(max_length=50)
    port = models.IntegerField(default=1001)
    timeout = models.FloatField(default=30.0)

    def __str__(self):
        return self.protocol_type

    def start_data_collection(self):
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        register_start_address = 68
        total_registers = 2

        message_send = struct.pack("2B", 0x01, 0x03) + struct.pack(">2H", register_start_address, total_registers)

        crc = self._computate_crc(message_send)

        message_send = message_send + crc

        alarm = VoltageObserver()

        try:
            thread.start_new_thread(self._thread_data_collection, (new_socket, message_send, alarm))
        except:
            print "Can't create thread"

        return True

    def _thread_data_collection(self, socket, message_send, alarm):
        i = 0
        while(i < 10):
            socket.sendto(message_send, (self.transductor.ip_address, self.port))
            message_received = socket.recvfrom(256)

            value = self._get_value_from_response_message(message_received[0])

            alarm.observe('new data received', alarm.verify_voltage)
            Event('new data received', value)

            self.transductor.measurements_set.create(voltage_a=value, collection_date=timezone.now())

            i = i + 1
            time.sleep(1)

    def _get_value_from_response_message(self, message_received_data):
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

    def _computate_crc(self, message_send):
        crc = 0xFFFF
        for index, item in enumerate(bytearray(message_send)):
            next_byte = item
            crc ^= next_byte
            for i in range(8):
                lsb = crc & 1
                crc >>= 1
                if lsb:
                    crc ^= 0xA001
        final_crc = struct.pack("<H", crc)

        return final_crc


class Measurements(models.Model):

    transductor = models.ForeignKey(Transductor, on_delete=models.CASCADE)
    voltage_a = models.FloatField(default=None)
    collection_date = models.DateTimeField('date published')

    def __str__(self):
        return '%s' % self.voltage_a

@receiver(post_save, sender=Transductor)
def transductor_saved(sender, instance, **kwargs):
    if instance.data_collection:
        print "true"
        # instance.communicationprotocol_set.first().restart_data_collection()
    else:
        instance.communicationprotocol_set.first().start_data_collection()