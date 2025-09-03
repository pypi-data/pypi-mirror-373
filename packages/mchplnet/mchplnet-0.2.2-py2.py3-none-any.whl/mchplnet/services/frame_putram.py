"""This module writes user defined values to target memory address."""

from mchplnet.lnetframe import LNetFrame


class FramePutRam(LNetFrame):
    """FramePutRam is responsible for setting up the request frame for MCU to 'Set' the variable value."""

    def __init__(self, address: int, size: int, width: int, value: bytearray = None):
        """Initialize the FramePutRam instance.

        Args:
            address (int): Address of the variable.
            size (int): Size of the variable.
            value (bytearray, optional): Value to set on the defined variable in bytes.
            width (int): Width according to the type of microcontroller.
        """
        super().__init__()
        self.value_dataType = width
        self.service_id = 10
        self.address = address
        self.size = size
        self.value = bytearray() if value is None else value

    def _get_data(self):
        byte_address = self.address.to_bytes(length=self.value_dataType, byteorder="little")
        self.data.extend([self.service_id, *byte_address, self.size, *self.value])

    def set_all(self, address: int, size: int, value: bytearray) -> None:
        """Set all parameters manually of the frame.

        Args:
            address (int): Address of the variable.
            size (int): Size of the variable.
            value (bytearray): Value to set on the defined variable in bytes.
        """
        self.address = address
        self.size = size
        self.value = value

    def set_size(self, size: int):
        """Set the size of the variable (Bytes).

        Args:
            size (int): Size of the variable.
        """
        self.size = size

    def get_size(self) -> int:
        """Get the size of the variable.

        Returns:
            int: Size of the variable.
        """
        return self.size

    def set_address(self, address: int):
        """Set manually the address of the variable.

        Args:
            address (int): Address of the variable.
        """
        self.address = address

    def get_address(self) -> int:
        """Get the memory address of the variable.

        Returns:
            int: Address of the variable.
        """
        return self.address

    def set_user_value(self, value: bytearray):
        """Set the user-defined value for the specific variable.

        Args:
            value (bytearray): User-defined value for the specific variable.
        """
        self.value = value

    def get_user_value(self) -> bytearray:
        """Get the user-defined value for the specific variable.

        Returns:
            int: User-defined value for the specific variable.
        """
        return self.value

    def _deserialize(self):
        """Deserialization of received bytes.

        Nothing to do here once there is no service data on put ram and
        errors and service id have already being checked by the superclass
        """
