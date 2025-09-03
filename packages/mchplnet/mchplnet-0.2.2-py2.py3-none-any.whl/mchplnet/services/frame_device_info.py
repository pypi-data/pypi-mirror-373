"""This module defines a custom frame for device information retrieval and interpretation.

This frame is responsible for Hand-Shake, Monitor-Version, Identifying processor Type, and Application Version.
It extracts various parameters related to the device, such as monitor version, application version, processor ID,
monitor date, DSP state, microcontroller width, etc.

Usage:
    - Ensure that the necessary imports from external modules are satisfied.
    - The class `FrameDeviceInfo` inherits from `LNetFrame`, which is not provided in this module.
      Make sure to import the required module or define the `LNetFrame` class to use this module properly.
    - Utilize the `FrameDeviceInfo` class to deserialize received data and retrieve device information.

"""

import logging
from dataclasses import dataclass
from typing import ClassVar

from mchplnet.lnetframe import LNetFrame


@dataclass
class DeviceInfo:
    monitor_version: int = 0
    appVer: int = 0
    maxTargetSize = 0
    processor_id: int = 0
    monitorDate: int = 0
    monitorTime: int = 0
    appDate: int = 0
    appTime: int = 0
    uc_width: int = 0
    dsp_state: int = 0
    eventType: int = 0
    eventID: int = 0
    tableStructAdd: int = 0
    MACHINE_16: ClassVar[int] = 2
    MACHINE_32: ClassVar[int] = 4


# noinspection PyTypeChecker
class FrameDeviceInfo(LNetFrame):
    """Custom frame for device information retrieval and interpretation.
    Inherits from LNetFrame.
    """

    def __init__(self):
        """Initialize the FrameDeviceInfo class.
        """
        super().__init__()
        self.service_id = 0

    def _get_data(self):
        self.data.append(self.service_id)

    def _get_processor_id(self):
        """Maps the microcontroller ID to the corresponding value.

        Returns:
            int: Microcontroller width (2 for 16-bit uc or 4 for 32-bit uc) or None if not in the list of uc defined.
        """
        value = int.from_bytes(self.received[10:12], byteorder="little")
        hex_value = hex(value)

        processor_ids_16_bit = {
            "0x8210": "__GENERIC_MICROCHIP_DSPIC__",
            "0x8230": "__GENERIC_MICROCHIP_PIC24__",
            "0x0221": "__DSPIC33FJ256MC710__",
            "0x0222": "__DSPIC33FJ128MC706__",
            "0x0223": "__DSPIC33FJ128MC506__",
            "0x0224": "__DSPIC33FJ64GS610__",
            "0x0225": "__DSPIC33FJ64GS406__",
            "0x0226": "__DSPIC33FJ12GP202__",
            "0x0228": "__DSPIC33FJ128MC802__",
            "0x0231": "__DSPIC33EP256MC506__",
            "0x0232": "__DSPIC33EP128GP502__",
            "0x0233": "__DSPIC33EP32GP502__",
            "0x0234": "__DSPIC33EP256GP502__",
            "0x0235": "__DSPIC33EP256MC502__",
            "0x0236": "__DSPIC33EP128MC202__",
            "0x0237": "__DSPIC33EP128GM604__",
        }

        processor_ids_32_bit = {
            "0x8240": "X2C_GENERIC_MICROCHIP_DSPIC33A",
            "0x8220": "__GENERIC_MICROCHIP_PIC32__",
            "0x8320": "__GENERIC_ARM_ARMV6__",
            "0x8310": "__GENERIC_ARM_ARMV7__",
            "0x0241": "__PIC32MZ2048EC__",
            "0x0251": "__PIC32MX170F256__",
        }


        if hex_value in processor_ids_16_bit:
            logging.info(f"Processor is: {processor_ids_16_bit.get(hex_value)} :16-bit")
            DeviceInfo.processor_id = processor_ids_16_bit.get(hex_value)
            return 2
        elif hex_value in processor_ids_32_bit:
            logging.info(f"Processor is: {processor_ids_32_bit.get(hex_value)} :32-bit")
            DeviceInfo.processor_id = processor_ids_32_bit.get(hex_value)
            return 4
        else:
            logging.error("Processor is: Unknown")
            return None

    def _deserialize(self):
        DeviceInfo.appVer = self._app_ver()
        DeviceInfo.monitor_version = self._monitor_ver()
        DeviceInfo.uc_width = self._get_processor_id()
        DeviceInfo.monitorDate = self._monitor_date()
        DeviceInfo.monitorTime = self._monitor_time()
        DeviceInfo.appDate = self._app_date()
        DeviceInfo.appTime = self._app_time()
        DeviceInfo.dsp_state = self._dsp_state()
        DeviceInfo.eventType = self._event_type()
        DeviceInfo.eventID = self._event_id()
        DeviceInfo.tableStructAdd = self._table_struct_add()

        return DeviceInfo

    def _app_ver(self):
        """Get the application version.

        Returns:
            int: The application version data.
        """
        return int.from_bytes(self.received[7:9], byteorder="little")

    def _monitor_ver(self):
        """Get the monitor version.

        Returns:
            int: The monitor version data.
        """
        return int.from_bytes(self.received[5:7], byteorder="little")

    def _monitor_date(self):
        """Extract and convert monitor date and time from the received data.

        Returns:
            str: Monitor date and time as a string.
        """
        return "".join([chr(val) for val in self.received[12:21]])

    def _monitor_time(self):
        """Extract and convert monitor date and time from the received data.

        Returns:
            str: Monitor date and time as a string.
        """
        return "".join([chr(val) for val in self.received[21:25]])

    def _app_date(self):
        """Extract and convert monitor date from the received data.

        Returns:
            str: Monitor date as a string.
        """
        return "".join([chr(val) for val in self.received[25:34]])

    def _app_time(self):
        """Extract and convert monitor time from the received data.

        Returns:
            str: Monitor time as a string.
        """
        return "".join([chr(val) for val in self.received[34:38]])

    def _dsp_state(self):
        """The DSP state indicates the current state of X2C.

        Returns:
            "MONITOR - Monitor runs on target but no application".
            "APPLICATION LOADED - Application runs on target (X2Cscope Update function is being executed)".
            "IDLE - Application is idle (X2Cscope Update Function is not being executed)".
            "INIT - Application is initializing and usually changes to state 'IDLE' after being finished".
            "APPLICATION RUNNING - POWER OFF - Application is running with disabled power electronics".
            "APPLICATION RUNNING - POWER ON - Application is running with enabled power electronics".
        """
        dsp_state = {
            0x00: "Monitor runs on target but no application",
            0x01: "Application runs on target",
            0x02: "Application is idle",
            0x03: "Application is initializing and usually changes to state 'IDLE' after being finished",
            0x04: "POWER OFF",
            0x05: "POWER ON",
        }
        return dsp_state.get(self.received[38], "Unknown DSP State")

    def _event_type(self):
        """Get the monitor version.

        Returns:
            int: The monitor version.
        """
        return int.from_bytes(self.received[39:41], byteorder="little")

    def _event_id(self):
        """Get the monitor version.

        Returns:
            int: The monitor version data.
        """
        return int.from_bytes(self.received[41:45], byteorder="little")

    def _table_struct_add(self):
        """Get the table structure add.

        Returns:
            int: The table structure add.
        """
        return int.from_bytes(self.received[45:49], byteorder="little")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
