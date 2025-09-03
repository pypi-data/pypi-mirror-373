"""Example to configure and getting started with receiving variable Value using watchView functionality."""

import logging

from mchplnet.interfaces.factory import InterfaceFactory
from mchplnet.interfaces.factory import InterfaceType as IType
from mchplnet.lnet import LNet

# Configure logging to aid in debugging
logging.basicConfig(level=logging.DEBUG)

# Create an interface instance for communication with the microcontroller.
# Here, we are using a serial interface with specified port and baud-rate.
interface = InterfaceFactory.get_interface(IType.SERIAL, port="COM16", baudrate=115200)

# LNet is responsible for managing low-level communication with the microcontroller.
l_net = LNet(interface)

# Logging various information about the connected device.
logging.debug(l_net.device_info.monitorDate)
logging.debug(l_net.device_info.processor_id)
logging.debug(l_net.device_info.uc_width)
logging.debug(f"appversion:{l_net.device_info.appVer}....... DSP state:{l_net.device_info.dsp_state}")

# Reading a specific memory address from the RAM of the microcontroller.
# here we provide manually the address and the data type of the variable.
read_bytes = l_net.get_ram(4148, 2)

# Convert the read bytes to an integer for easier interpretation.
# The byte order is specified as 'little-endian'.
logging.debug(int.from_bytes(read_bytes, byteorder="little"))

# The following code is commented out. If executed, it would write a value to a specific memory address.
# put_value = l_net.put_ram(4148, 2, bytes(50))
# logging.debug(put_value)
