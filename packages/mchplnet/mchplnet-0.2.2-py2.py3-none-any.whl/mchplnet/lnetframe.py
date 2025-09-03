import logging
from abc import ABC, abstractmethod


class LNetFrame(ABC):
    """LNetFrame is an abstract base class that implements the structure of LNet frames.

    LNet frames consist of several parts, including SYN, SIZE, NODE, DATA, and CRC.
    the SYN byte indicates the start of a frame and is always 0x55.
    the SIZE byte
    represents the number of data bytes in the frame.
    the NODE byte identifies the
    target slave node.
    the DATA area contains the frame's data, and the CRC byte is
    used for error checking.

    Attributes:
        received (bytearray): The received frame data.
        service_id (int): The Service ID identifying the type of service.
        __syn (int): The SYN byte value (always 0x55).
        __node (int): The NODE byte value (default is 1).
        data (list): The data part of the frame.
        crc (int): The calculated CRC value for the frame.

    Methods:
        _get_data(self) -> list:
            Abstract method to be implemented by subclasses.
            returns the data part of the frame.

        serialize(self) -> bytearray:
            Serialize the frame and add SYN, SIZE, NODE, DATA, and CRC bytes.

        _crc_checksum(self, list_crc) -> int:
            Calculate a checksum from the contents of a list.

        _fill_bytes(self, frame) -> list:
            Handle reserved key values (0x55 and 0x02) in SIZE, NODE, or DATA areas.

        _crc_check(self, received) -> int:
            Check the CRC of the received frame.

        frame_integrity(self) -> bool:
            Check the integrity of the received frame by verifying the CRC.

        _check_id(self) -> bool:
            Check the Service ID and error status in the received frame.

        remove_fill_byte(self):
            Remove fill bytes (0x00) from the received frame.

        _deserialize(self, received):
            Abstract method to be implemented by subclasses.
            deserialize the frame data.

        error_id(error_id) -> str:
            Get the error description based on the error ID.

        deserialize(self, received) -> None or object:
            Save the parameters and check for errors in the received frame.
    """

    def __init__(self):
        """Initialize an LNetFrame instance."""
        self.received = None
        self.service_id = None
        self.__syn = 85
        self.__node = 1
        self.data = []  # data
        self.crc = None

    @abstractmethod
    def _get_data(self):
        """Append service payload to the member class self.data.

        This method is called by LNetFrame serialize method retrieving specific information from the subclass
        specialization. When this method is called, self.data is empty and the service needs to append its own
        data to the data member class
        """
        pass

    def serialize(self):
        """Serialize the frame by setting up SYN, SIZE, NODE, DATA, and CRC bytes.

        Returns:
            bytearray: Serialized frame.
        """
        self.data.clear()  # clear the data array
        self._get_data()  # Get data from the subclass (actual service)
        frame_size = len(self.data)  # Get the length of the data frame
        self.data[:0] = [self.__syn, frame_size, self.__node]  # prepend frame bytes
        self.data.append(self._crc_checksum(self.data))
        self._add_fill_byte()
        return bytearray(self.data)

    def _crc_checksum(self, list_crc):
        """Calculate a checksum from the contents of a list.

        Args:
            list_crc (list): List of integers to calculate the CRC from.

        Returns:
            int: Calculated CRC.
        """
        sum_of_frame_data = sum(list_crc)  # Summing the list (int)

        crc_calculation = sum_of_frame_data % 256  # Calculate modulo

        logging.debug("Checksum: {}".format(crc_calculation))

        # Checksum 0x55 == 0xAA   85 == 170
        # Checksum 0x02 == 0xFD   02 == 253 (INVERTED)
        if crc_calculation == 85:
            crc_calculation = 170
        elif crc_calculation == 2:
            crc_calculation = 253

        self.crc = crc_calculation  # Add the hex checksum to the list of the data

        logging.debug("Calculated CRC for the frame: {}  Based on: {}".format(self.crc, list_crc))

        return self.crc

    def _add_fill_byte(self):
        """Handle reserved key values 0x55 and 0x02 in SIZE, NODE, or DATA areas.

        If any of these key values occur within SIZE, NODE, or DATA area, a 0x00 'fill_bytes'
        will be added, which will not be counted as data size and not be used in checksum calculation.
        """
        i = 1
        while i < len(self.data):
            if self.data[i] == 0x02 or self.data[i] == 0x55:
                self.data.insert(i + 1, 0x00)
            i += 1

    def frame_integrity(self) -> bool:
        """Check the integrity of the received frame by verifying the CRC.

        Returns:
            bool: True if the frame integrity check passes, False otherwise.
        """
        if self._crc_checksum(self.received[:-1]) != self.received[-1]:
            logging.error("CRC Checksum doesn't match: {}".format(self._crc_checksum(self.received)))
            return False
        return True

    @abstractmethod
    def _deserialize(self):
        """Deserialize the frame data stored on class member 'received'.

        Returns: None or object: Deserialize frame for the respected service ID and provide required Data or None if
        there are errors.
        """
        pass

    def _check_frame_protocol(self):
        """Check the Service ID and error status in the received frame.

        Returns:
            bool: True if the Service ID and error status are valid, False otherwise.
        """
        logging.debug(self.get_error_id(self.received[4]))
        return self.received[3] == self.service_id and self.received[4] == 0

    def _remove_fill_byte(self):
        """Remove fill bytes (0x00) from the received frame."""
        z = 1
        while z < len(self.received):
            if self.received[z] == 0x55 or self.received[z] == 0x02:
                self.received.pop(z + 1)
            z += 1

    def deserialize(self):
        """Save the parameters and check for errors in the response frame.

        Returns:
            None or object: Deserialized frame or None if there are errors.
        """
        self._remove_fill_byte()
        if self.frame_integrity() and self._check_frame_protocol():
            return self._deserialize()
        logging.error("Error on frame integrity or frame not correct!")
        return None

    @staticmethod
    def get_error_id(error_id: int):
        """Get the error description based on the error ID.

        Args:
            error_id (int): Error ID.

        Returns:
            str: Error description.
        """
        _error_id = {
            0: "No Error",
            19: "Checksum Error",
            20: "Format Error",
            21: "Size too large",
            33: "Service not available",
            34: "Invalid DSP state",
            48: "Flash write error",
            49: "Flash write protect error",
            64: "Invalid Parameter ID",
            65: "Invalid Block ID",
            66: "Parameter Limit error",
            67: "Parameter table not initialized",
            80: "Power-on Error",
        }
        try:
            __error_id = _error_id[error_id]
        except IndexError:
            logging.error("Unknown Error")
            logging.error("Valid index numbers are: " + str(list(_error_id.keys())))
            return
        return _error_id[error_id]


if __name__ == "__main__":
    logging.debug("Elf_parser.__name__")
