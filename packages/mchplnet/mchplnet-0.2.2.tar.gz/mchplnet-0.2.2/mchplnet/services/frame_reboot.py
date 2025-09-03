
from mchplnet.lnetframe import LNetFrame

class FrameReboot(LNetFrame):
    """Custom frame for device information retrieval and interpretation. Inherits from LNetFrame."""

    def __init__(self):
        """Initialize the FrameDeviceInfo class."""
        super().__init__()
        self.service_id = 25

    def _get_data(self):
        self.data.append(self.service_id)


    def _deserialize(self):
        """Deserialization of bytes received from device.

        Nothing to do here once there is no service data on save parameter and
        errors and service id have already being checked by the superclass
        """