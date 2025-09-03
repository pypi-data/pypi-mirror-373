import logging

from mchplnet.interfaces.abstract_interface import InterfaceABC
from mchplnet.services.frame_device_info import DeviceInfo, FrameDeviceInfo
from mchplnet.services.frame_getram import FrameGetRam
from mchplnet.services.frame_load_parameter import FrameLoadParameter, LoadScopeData
from mchplnet.services.frame_putram import FramePutRam
from mchplnet.services.frame_save_parameter import FrameSaveParameter, ScopeSetup
from mchplnet.services.frame_reboot import FrameReboot


class LNet:
    """LNet is a class that handles communication with a microcontroller.

    This class facilitates interface handshake, retrieving device information, saving and loading scope parameters,
    and reading/writing data to the microcontroller's RAM.
    """

    def __init__(self, interface: InterfaceABC, handshake: bool = True):
        """Initialize the LNet instance.

        Args:
            interface (InterfaceABC): The interface for communication with the microcontroller.
            handshake (bool, optional): If True, performs an interface handshake upon initialization. Defaults to True.
        """
        self.scope_data = None
        self.interface = interface
        self.device_info = None
        self.scope_setup = ScopeSetup()
        if handshake:
            self._handshake()

    def _handshake(self):
        """Perform an interface handshake and retrieve device information.

        Raises:
            RuntimeError: If unable to retrieve device information successfully.
        """
        try:
            self.get_device_info()
            self.load_parameters()
        except Exception as e:
            logging.error(e)
            raise RuntimeError("Failed to retrieve device information.")

    def get_device_info(self) -> DeviceInfo:
        """Retrieve and return the device information.

        Returns:
            DeviceInfo: The device information retrieved from the microcontroller.
        """
        if not self.device_info:
            device_info_frame = FrameDeviceInfo()
            device_info_frame.received = self._read_data(device_info_frame.serialize())
            self.device_info = device_info_frame.deserialize()
        return self.device_info



    def reboot_device(self):
        """Retrieve and return the device information.

        Returns:
            DeviceInfo: The device information retrieved from the microcontroller.
        """
        self._check_device_info()
        reboot_device = FrameReboot()
        print(reboot_device.serialize())
        reboot_device.received = self._read_data(reboot_device.serialize())
        return reboot_device.received

    def _check_device_info(self):
        """Check if the device information is initialized.

        Raises:
            RuntimeError: If the device information has not been initialized.
        """
        if self.device_info is None:
            raise RuntimeError("DeviceInfo is not initialized. Call get_device_info() first.")

    def save_parameter(self):
        """Save the current scope configuration parameters to the microcontroller.

        Returns:
            The response from the microcontroller.

        Raises:
            RuntimeError: If device information is not retrieved before saving parameters.
        """
        self._check_device_info()
        frame_save_param = FrameSaveParameter()
        frame_save_param.set_scope_setup(self.scope_setup)
        frame_save_param.received = self._read_data(frame_save_param.serialize())
        return frame_save_param.deserialize()

    def load_parameters(self) -> LoadScopeData:
        """Load and return the scope parameters from the microcontroller.

        Returns:
            LoadScopeData: The loaded scope parameters.

        Raises:
            RuntimeError: If device information is not retrieved before loading parameters.
        """
        self._check_device_info()
        frame_load_param = FrameLoadParameter()
        frame_load_param.received = self._read_data(frame_load_param.serialize())
        self.scope_data = frame_load_param.deserialize()
        return self.scope_data

    def get_ram_array(self, address: int, bytes_to_read: int, data_type: int):
        """Read an array of data from the microcontroller's RAM.

        Args:
            address (int): The starting address in RAM to read data from.
            bytes_to_read (int): The number of bytes to read.
            data_type (int): The data type to read.

        Returns:
            An array of data read from RAM.

        Raises:
            RuntimeError: If device information is not retrieved before reading RAM.
        """
        self._check_device_info()
        get_ram_frame = FrameGetRam(address, bytes_to_read, data_type, self.device_info.uc_width)
        get_ram_frame.received = self._read_data(get_ram_frame.serialize())
        return get_ram_frame.deserialize()

    def get_ram(self, address: int, data_type: int) -> bytearray:
        """Read data from the microcontroller's RAM.

        Args:
            address (int): The address to read data from in the microcontroller's RAM.
            data_type (int): The data type (number of bytes) to read.

        Returns:
            bytearray: The data read from the RAM.

        Raises:
            RuntimeError: If device information is not retrieved before reading RAM.
        """
        self._check_device_info()
        get_ram_frame = FrameGetRam(address, data_type, data_type, self.device_info.uc_width)
        get_ram_frame.received = self._read_data(get_ram_frame.serialize())
        return get_ram_frame.deserialize()

    def put_ram(self, address: int, size: int, value: bytearray):
        """Write data to the microcontroller's RAM.

        Args:
            address (int): The address in the microcontroller's RAM to write data to.
            size (int): The size (number of bytes) of the data to write.
            value (bytearray): The data to be written to RAM.

        Returns:
            The response from the microcontroller.

        Raises:
            RuntimeError: If device information is not retrieved before writing to RAM.
        """
        self._check_device_info()
        put_ram_frame = FramePutRam(address, size, self.device_info.uc_width, value)
        put_ram_frame.received = self._read_data(put_ram_frame.serialize())
        return put_ram_frame.deserialize()

    def _read_data(self, frame):
        """Send a frame to the microcontroller and read the response.

        Args:
            frame: The frame data to be sent.

        Returns:
            The response from the microcontroller.
        """
        self.interface.write(frame)
        return self.interface.read()

    def get_scope_setup(self) -> ScopeSetup:
        """Get the current scope setup.

        Returns:
            ScopeSetup: The current scope setup instance.
        """
        return self.scope_setup
