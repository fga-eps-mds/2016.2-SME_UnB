from __future__ import unicode_literals

from django.db import models
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField


class TransductorModel(models.Model):
    name = models.CharField(max_length=50, unique=True)
    internet_protocol = models.CharField(max_length=50)
    serial_protocol = models.CharField(max_length=50)
    register_addresses = ArrayField(models.IntegerField())

    def __str__(self):
        return self.name


class Transductor(models.Model):
    model = models.ForeignKey(TransductorModel)
    serie_number = models.IntegerField(default=None)
    ip_address = models.CharField(max_length=15, unique=True, validators=[
        RegexValidator(
            regex='^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
            message='Incorrect IP address format',
            code='invalid_ip_address'
        ),
    ])
    description = models.TextField(max_length=150)
    creation_date = models.DateTimeField('date published')

    class Meta:
        abstract = True
        permissions = (
            ("can_view_transductors", "Can view Transductors Page"),
        )

class EnergyTransductor(Transductor):

    def __str__(self):
        return self.description


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

        return ap_total
