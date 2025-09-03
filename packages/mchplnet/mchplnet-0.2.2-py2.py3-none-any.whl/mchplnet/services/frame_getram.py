"""Implements the FrameGetRam functionality to read values from target memory address."""

from mchplnet.lnetframe import LNetFrame


class FrameGetRam(LNetFrame):
    """Class implementation for 'GetRam' frame in the LNet protocol.

    This frame is responsible for setting up the request frame for the MCU to 'Get' the variable value.
    """

    def __init__(self, address: int, read_size: int, data_type: int, uc_width: int):
        """Initialize the FrameGetRam instance.

        Args:
            address (int): Address of the variable.
            read_Size (int): number of bytes to be read by the frame from microcontroller.
            uc_width (int): Width of the variable from microcontroller (in bytes).
            value_dataType(int): describes the type of the variable (1: 8-bit, 2:16-bit, 4:32-bit)
        """
        super().__init__()

        self.service_id = 9
        self.address = address
        self.read_size = read_size
        self.uc_width = uc_width
        self.value_data_type = data_type

    def _get_data(self):
        byte_address = self.address.to_bytes(length=self.uc_width, byteorder="little")
        self.data.extend([self.service_id, *byte_address, self.read_size, self.value_data_type])

    def _deserialize(self):
        # Extract the size of the received data
        # [SYN, SIZE, NODE, DATA, CRC]
        # DATA = [Service-ID, Error-ID, Service data]
        size_received_data = self.received[1]
        # Position of initial Service data bytes
        service_data_begin = 5
        # Calculate the size of Service data
        service_data_end = service_data_begin + size_received_data - 2

        # Check if received data size is valid
        if service_data_end <= service_data_begin:
            raise ValueError("Received data size is invalid.")

        # Extract the data bytes
        return self.received[service_data_begin:service_data_end]

    def set_size(self, size: int):
        """Set the size of the variable for the LNET frame for GetRamBlock.

        Args:
            size (int): Size of the variable.
        """
        self.read_size = size

    def get_size(self):
        """Get the size of the variable.

        Returns:
            int: Size of the variable.
        """
        return self.read_size

    def set_address(self, address: int):
        """Set the address of the variable.

        Args:
            address (int): Address of the variable.
        """
        self.address = address

    def get_address(self):
        """Get the address of the variable.

        Returns:
            int: Address of the variable.
        """
        return self.address
