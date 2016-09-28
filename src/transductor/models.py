from __future__ import unicode_literals
from polymorphic.manager import PolymorphicManager
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import FieldError
from polymorphic.models import PolymorphicModel
import numpy


class TransductorModel(models.Model):
    """
        Class responsible to define a transductor model which contains crucial informations about the
        transductor itself.

        Attributes:
            - name(str): The factory name.
            - internet_protocol(str): The internet protocol.
            - serial_protocol(str): The serial protocol.
            - register_addresses(list): Registers with data to be collected.
                .. note::
                    This attribute must meet the following pattern:

                    [[Register Address(int), Register Type(int)]]

                Where:
                    - Register Address: register address itself.
                    - Register Type: register data type.
                        - 0 - Integer
                        - 1 - Float

                Example: [[68, 0], [70, 1]]

        Example of use:

        >>> TransductorModel(name="Test Name", internet_protocol="UDP", serial_protocol="Modbus RTU", register_addresses=[[68, 0], [70, 1]])
        <TransductorModel: Test Name>
    """
    name = models.CharField(max_length=50, unique=True)
    internet_protocol = models.CharField(max_length=50)
    serial_protocol = models.CharField(max_length=50)
    register_addresses = ArrayField(ArrayField(models.IntegerField()))

    def __str__(self):
        return self.name


class Transductor(models.Model):
    """
        Base class responsible to create an abstraction of a transductor.

        Attributes:
            - model(TransductorModel): The transductor model.
            - serie_number(int): The serie number.
            - ip_address(str): The ip address.
            - description(str): A succint description.
            - creation_date(datetime): The exactly creation time.
    """
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
    creation_date = models.DateTimeField('date published', auto_now=True)

    class Meta:
        abstract = True


class EnergyTransductor(Transductor):
    """
        Class responsible to represent a Energy Transductor which will collect energy measurements.

        Example of use:

        >>> from django.utils import timezone
        >>> t_model = TransductorModel(name="Test Name", internet_protocol="UDP", serial_protocol="Modbus RTU", register_addresses=[[68, 0], [70, 1]])
        >>> EnergyTransductor(model=t_model, serie_number=1, ip_address="1.1.1.1", description="Energy Transductor Test", creation_date=timezone.now())
        <EnergyTransductor: Energy Transductor Test>
    """
    def __str__(self):
        return self.description


class Measurements(PolymorphicModel):
    """
        Class responsible to create a base for measurements and optimize performance from queries
        using the django-polymorphic.

        .. note::

            It's not necessary create instances of this class.

        Attributes:
            - collection_date(datetime): The exactly collection time.
            - collection_minute(int): The minute from collection.

        Example of Polymorphic search using child class EnergyMeasurements:

        >>> from django.utils import timezone
        >>> t_model = TransductorModel.objects.create(name="Test Name", internet_protocol="UDP", serial_protocol="Modbus RTU", register_addresses=[[68, 0], [70, 1]])
        >>> e_transductor = EnergyTransductor.objects.create(model=t_model, serie_number=1, ip_address="1.1.1.1", description="Energy Transductor Test", creation_date=timezone.now())
        >>> time = timezone.now()
        >>> EnergyMeasurements.objects.create(transductor=e_transductor, voltage_a=122.875, voltage_b=122.784, voltage_c=121.611, current_a=22.831, current_b=17.187, current_c= 3.950, active_power_a=2.794, active_power_b=1.972, active_power_c=3.950, reactive_power_a=-0.251, reactive_power_b=-0.752, reactive_power_c=-1.251, apparent_power_a=2.805, apparent_power_b=2.110, apparent_power_c=4.144, collection_date=time, collection_minute=time.minute)
        <EnergyMeasurements: 2016-09-15 21:30:53.522540+00:00>
        >>> Measurements.objects.all()
        [<EnergyMeasurements: 2016-09-15 21:30:53.522540+00:00>]
        >>> Measurements.objects.instance_of(EnergyMeasurements)
        [<EnergyMeasurements: 2016-09-15 21:30:53.522540+00:00>]

        Click `here <https://django-polymorphic.readthedocs.io/en/stable/quickstart.html>`_ to see full django-polymorphic documentation.
    """
    collection_date = models.DateField('date published', auto_now=True)
    collection_minute = models.IntegerField(default=None)


class EnergyMeasurementsManager(PolymorphicManager):
    def annual(self, year, *args):
        qs = self.get_queryset().filter(collection_date__year=year)

        try:
            data = qs.values_list(*args).all()
        except FieldError:
            raise

        return numpy.array(data)

    def monthly(self, year, month, *args):
        qs = self.get_queryset().filter(collection_date__year=year, collection_date__month=month)

        try:
            data = qs.values_list(*args).all()
        except FieldError:
            raise

        return numpy.array(data)

    def daily(self, date, *args):
        qs = self.get_queryset().filter(collection_date=date)

        try:
            data = qs.values_list(*args).all()
        except FieldError:
            raise

        return numpy.array(data)


class EnergyMeasurements(Measurements):
    """
        Class responsible to store energy measurements, considering a three-phase energy system.

        Attributes:
            - voltage_a(float): The voltage on phase A.
            - voltage_b(float): The voltage on phase B.
            - voltage_c(float): The voltage on phase C.
            - current_a(float): The current on phase A.
            - current_b(float): The current on phase B.
            - current_c(float): The current on phase C.
            - active_power_a(float): The active power on phase A.
            - active_power_b(float): The active power on phase B.
            - active_power_c(float): The active power on phase C.
            - reactive_power_a(float): The reactive power on phase A.
            - reactive_power_b(float): The reactive power on phase B.
            - reactive_power_c(float): The reactive power on phase C.
            - apparent_power_a(float): The apparent power on phase A.
            - apparent_power_b(float): The apparent power on phase B.
            - apparent_power_c(float): The apparent power on phase C.

        Example of use:

        >>> from django.utils import timezone
        >>> t_model = TransductorModel.objects.create(name="Test Name", internet_protocol="UDP", serial_protocol="Modbus RTU", register_addresses=[[68, 0], [70, 1]])
        >>> e_transductor = EnergyTransductor.objects.create(model=t_model, serie_number=1, ip_address="1.1.1.1", description="Energy Transductor Test", creation_date=timezone.now())
        >>> EnergyMeasurements.objects.create(transductor=e_transductor, voltage_a=122.875, voltage_b=122.784, voltage_c=121.611, current_a=22.831, current_b=17.187, current_c= 3.950, active_power_a=2.794, active_power_b=1.972, active_power_c=3.950, reactive_power_a=-0.251, reactive_power_b=-0.752, reactive_power_c=-1.251, apparent_power_a=2.805, apparent_power_b=2.110, apparent_power_c=4.144, collection_minute=timezone.now().minute
        <EnergyMeasurements: 2016-09-15 21:30:53.522540+00:00>
    """
    mng_objects = EnergyMeasurementsManager()

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


class EnergyOperations(object):
    """
        Class responsible to perform energy mathematical operations.

        Atributtes:
            - energy_measurement(EnergyMeasurements): Energy measurements related to a specific instant of time.
    """
    def __init__(self, e_measurement):
        self.energy_measurement = e_measurement

    def calculate_total_active_power(self):
        """
            Instance method responsible to calculate the total active power of a time instant.

            :returns: float -- the total active power.
        """
        active_power_a = self.energy_measurement.active_power_a
        active_power_b = self.energy_measurement.active_power_b
        active_power_c = self.energy_measurement.active_power_c

        return (active_power_a + active_power_b + active_power_c)

    def calculate_total_reactive_power(self):
        """
            Instance method responsible to calculate the total reactive power of a time instant.

            :returns: float -- the total reactive power.
        """
        reactive_power_a = self.energy_measurement.reactive_power_a
        reactive_power_b = self.energy_measurement.reactive_power_b
        reactive_power_c = self.energy_measurement.reactive_power_c

        return (reactive_power_a + reactive_power_b + reactive_power_c)

    def calculate_total_apparent_power(self):
        """
            Instance method responsible to calculate the total apparent power of a time instant.

            :returns: float -- the total apparent power.
        """
        ap_phase_a = self.energy_measurement.apparent_power_a
        ap_phase_b = self.energy_measurement.apparent_power_b
        ap_phase_c = self.energy_measurement.apparent_power_c

        ap_total = (ap_phase_a + ap_phase_b + ap_phase_c)

        return ap_total
