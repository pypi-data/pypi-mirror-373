"""Factory interface implementation.

Usage: Ensures the proper configuration of the communication interface supported by X2Cscope.
"""

import logging
from enum import Enum

from mchplnet.interfaces.abstract_interface import InterfaceABC
from mchplnet.interfaces.can import LNetCan
from mchplnet.interfaces.lin import LNetLin
from mchplnet.interfaces.tcp_ip import LNetTcpIp
from mchplnet.interfaces.uart import LNetSerial


class InterfaceType(Enum):
    SERIAL = 1
    CAN = 2
    LIN = 3
    TCP_IP = 4


class InterfaceFactory:
    @staticmethod
    def get_interface(interface_type: InterfaceType, *args: object, **kwargs: object) -> InterfaceABC:
        interfaces = {
            InterfaceType.SERIAL: (
                LNetSerial,
                {
                    "port": "Serial port name or device path",
                },
            ),
            InterfaceType.CAN: (
                LNetCan,
                {"channel": "CAN channel number or identifier"},
            ),
            InterfaceType.LIN: (
                LNetLin,
                {"channel": "LIN channel number or identifier"},
            ),
            InterfaceType.TCP_IP: (
                LNetTcpIp,
                {
                    "host": "IP address or hostname of the remote device",
                    "port": "Port number for TCP/IP communication",
                },
            ),
        }

        interface_class, required_params = interfaces[interface_type]

        # TODO: required params should be a task of the interface, an not of the factory
        # if the parameter is not supplied, it should assume default values
        # Check if all required parameters are provided
        missing_params = [param for param, description in required_params.items() if param not in kwargs]
        if missing_params:
            raise ValueError(f"Missing required parameters for {interface_type.name}: {', '.join(missing_params)}")

        return interface_class(*args, **kwargs)


if __name__ == "__main__":
    interface = InterfaceType.SERIAL
    interface_kwargs = {"port": "COM8", "baud-rate": 115200}

    try:
        interface = InterfaceFactory.get_interface(interface, **interface_kwargs)
        logging.debug("Interface created: %s", interface)
    except ValueError as e:
        logging.debug("Error creating interface: %s", str(e))
