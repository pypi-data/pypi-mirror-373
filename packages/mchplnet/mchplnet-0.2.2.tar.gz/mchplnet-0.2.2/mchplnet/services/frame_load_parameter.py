"""Load Parameters frame definition.

The parameters loaded are used to get the Scope Data Array address 
and maximum size for once, as well as to check the current scope state.
"""

from dataclasses import dataclass

from mchplnet.lnetframe import LNetFrame


@dataclass
class LoadScopeData:
    """dataclass representing the loaded scope data.

    Attributes:
        scope_state (int): Value = zero if the scope is idle, and > zero if the scope is busy.
        num_channels (int): The number of active channels, max eight channels.
        sample_time_factor (int): Zero means to sample data at every Update function call.
                                  value 1 means to sample every 2nd call and so on.
        data_array_pointer (int): This value is for debug purposes only.
        it points to the next free location in the
                                  Scope Data Array for the next dataset to be stored.
                                  this value is an index, not a memory address.
        data_array_address (int): This value contains the memory address of the Scope Data Array.
        trigger_delay (int): The current trigger delay value.
        trigger_event_position (int): The position of the trigger event.
        data_array_used_length (int): The length of the used portion of the Scope Data Array.
        data_array_size (int): The total size of the Scope Data Array.
        scope_version (int): The version of the scope.
    """

    scope_state: int
    num_channels: int
    sample_time_factor: int
    data_array_pointer: int
    data_array_address: int
    trigger_delay: int
    trigger_event_position: int
    data_array_used_length: int
    data_array_size: int
    scope_version: int


class FrameLoadParameter(LNetFrame):
    """Class responsible for loading parameters using the LNet protocol."""

    def __init__(self):
        """Initialize the FrameLoadParameter instance."""
        super().__init__()
        self.address = None
        self.size = None
        self.service_id = 17
        self.unique_parameter = 1

    def _deserialize(self):
        data_bytes = self.received[5:-1]
        data_structure = [
            ("scope_state", 1),
            ("num_channels", 1),
            ("sample_time_factor", 2),
            ("data_array_pointer", 4),
            ("data_array_address", 4),
            ("trigger_delay", 4),
            ("trigger_event_position", 4),
            ("data_array_used_length", 4),
            ("data_array_size", 4),
            ("scope_version", 1),
        ]

        extracted_data = {}
        start_pos = 0
        for field, size in data_structure:
            extracted_data[field] = int.from_bytes(
                data_bytes[start_pos : start_pos + size],
                byteorder="little"
            )
            start_pos += size

        return LoadScopeData(**extracted_data)

    def _get_data(self):
        self.unique_parameter = self.unique_parameter.to_bytes(length=2, byteorder="little")
        self.data.extend([self.service_id, *self.unique_parameter])
