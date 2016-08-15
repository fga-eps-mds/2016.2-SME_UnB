from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.utils import timezone
from math import sqrt
import socket
import struct
import sys
import thread


class Transductor(models.Model):
    serie_number = models.IntegerField(default=None)
    ip_address = models.CharField(max_length=15)
    description = models.TextField(max_length=150)
    creation_date = models.DateTimeField('date published')
    data_collection = models.BooleanField(default=False)

    class Meta:
        abstract = True


class EnergyTransductor(Transductor):

    def __str__(self):
        return self.description

    def validate_unique_ip_address(self, exclude=None):
        energy_transductors = EnergyTransductor.objects.filter(ip_address=self.ip_address)

        if energy_transductors.filter(ip_address=self.ip_address).exists():
            raise ValidationError('Ip address must be unique per Energy Transductor')

    def save(self, *args, **kwargs):
        self.validate_unique_ip_address()

        super(EnergyTransductor, self).save(*args, **kwargs)


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
                packaged_message = struct.pack("2B", 0x01, 0x03) + struct.pack(">2H", initial_register, total_registers)

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

            # self.transductor.measurements_set.create(voltage_a=value, collection_date=timezone.now())

        collection_time = timezone.now()
        self._create_measurements_from_data_collected(messages, collection_time)

    def _create_measurements_from_data_collected(self, messages, collection_time):
        data = Measurements()

        data.transductor = self.transductor

        data.voltage_a = float("{0:.3f}".format(self._get_float_value_from_response(messages[0])))
        data.voltage_b = float("{0:.3f}".format(self._get_float_value_from_response(messages[1])))
        data.voltage_c = float("{0:.3f}".format(self._get_float_value_from_response(messages[2])))

        data.current_a = float("{0:.3f}".format(self._get_float_value_from_response(messages[3])))
        data.current_b = float("{0:.3f}".format(self._get_float_value_from_response(messages[4])))
        data.current_c = float("{0:.3f}".format(self._get_float_value_from_response(messages[5])))

        data.active_power_a = float("{0:.3f}".format(self._get_float_value_from_response(messages[6])))
        data.active_power_b = float("{0:.3f}".format(self._get_float_value_from_response(messages[7])))
        data.active_power_c = float("{0:.3f}".format(self._get_float_value_from_response(messages[8])))

        data.reactive_power_a = float("{0:.3f}".format(self._get_float_value_from_response(messages[9])))
        data.reactive_power_b = float("{0:.3f}".format(self._get_float_value_from_response(messages[10])))
        data.reactive_power_c = float("{0:.3f}".format(self._get_float_value_from_response(messages[11])))

        data.apparent_power_a = float("{0:.3f}".format(sqrt(data.active_power_a**2 + data.reactive_power_a**2)))
        data.apparent_power_b = float("{0:.3f}".format(sqrt(data.active_power_b**2 + data.reactive_power_b**2)))
        data.apparent_power_c = float("{0:.3f}".format(sqrt(data.active_power_c**2 + data.reactive_power_c**2)))

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

    collection_date = models.DateTimeField('date published')

    class Meta:
        abstract = True


class EnergyMeasurements(Measurements):

    transductor = models.ForeignKey(EnergyTransductor, on_delete=models.CASCADE)

    voltage_a = models.FloatField(default=None)
    voltage_b = models.FloatField(default=None)
    voltage_c = models.FloatField(default=None)

    current_a = models.FloatField(default=None)
    current_b = models.FloatField(default=None)
    current_c = models.FloatField(default=None)

    active_power_a = models.FloatField(default=None)
    active_power_b = models.FloatField(default=None)
    active_power_c = models.FloatField(default=None)

    reactive_power_a = models.FloatField(default=None)
    reactive_power_b = models.FloatField(default=None)
    reactive_power_c = models.FloatField(default=None)

    apparent_power_a = models.FloatField(default=None)
    apparent_power_b = models.FloatField(default=None)
    apparent_power_c = models.FloatField(default=None)

    def __str__(self):
        return '%s' % self.collection_date

    def calculate_total_active_power(self):
        return (self.active_power_a + self.active_power_b + self.active_power_c)

    def calculate_total_reactive_power(self):
        return (self.reactive_power_a + self.reactive_power_b + self.reactive_power_c)

    def calculate_total_apparent_power(self):
        ap_phase_a = self.apparent_power_a
        ap_phase_b = self.apparent_power_b
        ap_phase_c = self.apparent_power_c

        ap_total = (ap_phase_a + ap_phase_b + ap_phase_c)

        return '{0:.3f}'.format(ap_total)


@receiver(post_save, sender=Transductor)
def transductor_saved(sender, instance, **kwargs):
    if not instance.data_collection:
        instance.communicationprotocol_set.first().start_data_collection()
