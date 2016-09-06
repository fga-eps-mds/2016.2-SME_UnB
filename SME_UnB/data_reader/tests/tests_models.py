from django.test import TestCase

class ModBusRTUTestCase(TestCase):
    def setUp(self):
        t_model = TransductorModel()
        t_model.name = "TR 4020"
        t_model.internet_protocol = "UDP"
        t_model.serial_protocol = "Modbus RTU"
        t_model.register_addresses = [[68, 0], [70, 1]]
        t_model.save()

        transductor = EnergyTransductor()
        transductor.serie_number = "1"
        transductor.description = "Test"
        transductor.creation_date = timezone.now()
        transductor.model = t_model
        transductor.ip_address = "111.111.111.111"
        transductor.save()

    
