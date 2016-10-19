Data Reader Models

Models
=======

.. autoclass:: data_reader.models.SerialProtocol
    :members:

.. autoclass:: data_reader.models.ModbusRTU
    :members: create_messages, get_int_value_from_response, get_float_value_from_response, _computate_crc, _check_crc

.. autoclass:: data_reader.models.TransportProtocol
    :members:

.. autoclass:: data_reader.models.UdpProtocol
    :members:

.. autoclass:: data_reader.models.BrokenTransductorException
    :members:
