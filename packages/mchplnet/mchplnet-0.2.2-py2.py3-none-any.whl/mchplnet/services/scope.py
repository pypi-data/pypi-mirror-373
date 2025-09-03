"""Scope classes needed to implement scope functionality being called under frame_save_parameter."""

from dataclasses import dataclass
from typing import Dict
import struct

@dataclass
class ScopeChannel:
    """Represents a scope channel configuration.

    Attributes:
        name (str): The name of the channel.
        source_location (int): The memory address or source location of the channel data in the microcontroller.
        data_type_size (int): The size (in bytes) of the data type used by the channel.
        source_type (int): The source type identifier for the channel. Default is 0.
        is_integer (bool): Flag indicating if the data type is an integer. Default is False.
        is_signed (bool): Flag indicating if the data type is signed. Default is True.
        is_enable (bool): Flag indicating if the channel is enabled. Default is True.
        offset (int): Offset value for the data. Default is 0.
    """

    name: str
    source_location: int
    data_type_size: int = 0
    source_type: int = 0
    is_integer: bool = False
    is_signed: bool = True
    is_enable: bool = True
    offset: int = 0


@dataclass
class ScopeTrigger:
    """Scope trigger configuration.

    Attributes:
        channel (ScopeChannel): The channel to use as a trigger source.
        trigger_level (int): The level at which the trigger should activate.
        trigger_delay (int): The delay after the trigger activation before data collection starts.
        trigger_edge (int): Indicates the edge type for triggering (Rising Edge = 0x01, Falling Edge = 0x00).
        trigger_mode (int): The mode of triggering.
    """

    channel: ScopeChannel = None
    trigger_level: float = 0
    trigger_delay: int = 0
    trigger_edge: int = 1
    trigger_mode: int = 0


class ScopeSetup:
    """Represents a scope configuration setup.

    This class handles the configuration of the scope including channels, trigger settings,
    and managing the data buffer.

    Attributes:
        scope_state (int): The state of the scope. (0x02 for Auto without Trigger, 0x01 for Normal with Trigger).
        sample_time_factor (int): This parameter defines a pre-scaler when the Scope is in the sampling mode.
        This parameter can be used to extend the total sampling time at the cost of sampling resolution.
        channels (Dict[str, ScopeChannel]): Dictionary of scope channels keyed by their names.
        scope_trigger (ScopeTrigger): Configuration for the scope trigger.
    """

    def __init__(self):
        """Initializes a new instance of the ScopeSetup class."""
        self.scope_state = 2
        self.sample_time_factor = 1
        self.channels: Dict[str, ScopeChannel] = {}
        self.scope_trigger = ScopeTrigger()

    def set_sample_time_factor(self, sample_time_factor: int = 1):
        """Set the sample time factor for the scope. Default is 1.

        Args:
            sample_time_factor (int): The sample time factor to be set.
        """
        self.sample_time_factor = sample_time_factor

    def set_scope_state(self, scope_state: int = 2):
        """Set the scope state manually. 2 for Auto mode without Trigger, 1 for Normal mode with Trigger.

        Args:
            scope_state (int): The state to be set for the scope.
        """
        self.scope_state = scope_state

    def add_channel(self, channel: ScopeChannel, trigger: bool = False) -> int:
        """Add a new channel to the scope configuration.

        Args:
            channel (ScopeChannel): The channel to be added.
            trigger (bool): If True, sets this channel as the trigger source. Defaults to False.

        Returns:
            int: The total number of channels after addition or -1 if the limit is exceeded. Max allowed channels are 8.
        """
        if channel.name not in self.channels:
            if len(self.channels) > 8:
                return -1
            self.channels[channel.name] = channel
        if trigger:
            self.reset_trigger()
            self.scope_trigger.channel = channel
        return len(self.channels)

    def remove_channel(self, channel_name: str) -> int:
        """Remove a channel from the scope configuration.

        Args:
            channel_name (str): The name of the channel to be removed.

        Returns:
            int: the total number of channels after removal
        """
        if channel_name in self.channels:
            self.channels.pop(channel_name)
            if self.scope_trigger.channel and self.scope_trigger.channel.name == channel_name:
                self.reset_trigger()
        return len(self.channels)

    def get_channel(self, channel_name: str):
        """Get a channel by its name.

        Args:
            channel_name (str): The name of the channel to retrieve.

        Returns:
            ScopeChannel: The requested channel or None if not found.
        """
        if channel_name in self.channels:
            return self.channels[channel_name]
        return None

    def list_channels(self) -> Dict[str, ScopeChannel]:
        """List all channels in the scope configuration.

        Returns:
            Dict[str, ScopeChannel]: A dictionary of all channels.
        """
        return self.channels

    def reset_trigger(self):
        """Reset the trigger configuration to default."""
        self.scope_state = 2
        self.scope_trigger = ScopeTrigger()

    def set_trigger(self, scope_trigger: ScopeTrigger):
        """Set a custom trigger configuration.

        Args:
            scope_trigger (ScopeTrigger): The custom trigger configuration to be set.
        """
        self.scope_state = 1
        self.scope_trigger = scope_trigger

    def _trigger_level_to_bytes(self):
        """Convert user defined trigger level to a byte array.

        Returns:
            bytearray: The trigger level in byte format.
        """
        if self.scope_trigger.channel:
            if isinstance(self.scope_trigger.trigger_level, float):
                # Convert float to bytes using struct
                return struct.pack('<f', self.scope_trigger.trigger_level)
            else:
                # Assume it is an integer and use to_bytes
                return self.scope_trigger.trigger_level.to_bytes(
                    self.scope_trigger.channel.data_type_size,
                    byteorder="little",
                    signed=True,
                )
        else:
            return bytes(2)

    def get_dataset_size(self):
        """Calculate the size of the complete dataset from all channels.

        Returns:
            int: The total size of the dataset.
        """
        return sum(channel.data_type_size for channel in self.channels.values())

    def _trigger_delay_to_bytes(self):
        """Convert user defined trigger delay to a byte array.

        Returns:
            bytearray: The trigger delay in byte format.
        """
        sample_number = self.scope_trigger.trigger_delay * self.get_dataset_size()
        return sample_number.to_bytes(length=4, byteorder="little", signed=True)

    def get_buffer(self):
        """Get the buffer containing the current scope configuration.

        Returns:
            List[int]: A list consist of the scope configuration buffer.
        """
        if not self.channels:
            return []
        buffer = [
            self.scope_state,
            len(self.channels),
            self.sample_time_factor & 0xFF,
            (self.sample_time_factor >> 8) & 0xFF,
        ]

        for channel_name, channel in self.channels.items():
            if not channel.is_enable:
                continue
            buffer.append(channel.source_type)
            buffer.append(channel.source_location & 0xFF)
            buffer.append((channel.source_location >> 8) & 0xFF)
            buffer.append((channel.source_location >> 16) & 0xFF)
            buffer.append((channel.source_location >> 24) & 0xFF)
            buffer.append(channel.data_type_size)

        buffer.extend(self._get_scope_trigger_buffer())  # add scope trigger
        return buffer

    def _get_scope_trigger_buffer(self):
        """Get the buffer for the scope trigger configuration.

        Returns:
            List[int]: A list consist of the scope trigger configuration buffer.
        """
        if self.scope_trigger.channel:
            buffer = [
                self._get_trigger_data_type(),
                self.scope_trigger.channel.source_type,
                self.scope_trigger.channel.source_location & 0xFF,
                (self.scope_trigger.channel.source_location >> 8) & 0xFF,
                (self.scope_trigger.channel.source_location >> 16) & 0xFF,
                (self.scope_trigger.channel.source_location >> 24) & 0xFF,
            ]
        else:
            buffer = [self._get_trigger_data_type(), 0, 0, 0, 0, 0]

        buffer.extend(self._trigger_level_to_bytes())
        buffer.extend(self._trigger_delay_to_bytes())
        buffer.extend([self.scope_trigger.trigger_edge, self.scope_trigger.trigger_mode])
        return buffer

    def _get_trigger_data_type(self):
        """Get the data type for the scope trigger.

        Returns:
            int: The trigger data type.
        """
        ret = 0x80  # Bit 7 is always set because of "New Scope Version"
        if self.scope_trigger.channel:
            ret += 0x20 if self.scope_trigger.channel.is_signed else 0
            ret += 0x00 if self.scope_trigger.channel.is_integer else 0x10
            ret += self.scope_trigger.channel.data_type_size  # ._get_width()
        else:
            ret += 2  # ._get_width()

        return ret
