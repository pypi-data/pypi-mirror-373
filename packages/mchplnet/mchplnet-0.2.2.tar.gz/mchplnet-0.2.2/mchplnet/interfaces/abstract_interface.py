from abc import ABC, abstractmethod


class InterfaceABC(ABC):
    """An abstract base class defining the interface for a generic interface.

    This abstract base class (ABC) defines the methods and attributes that must be implemented by
    concrete interface classes. It serves as a blueprint for creating interface classes for various
    communication protocols.

    Attributes:
        None

    Methods:
        __init__(*args, **kwargs):
            Constructor for the interface. Subclasses should implement this method.

        __del__():
            Destructor for the interface. Stops the interface when the object is deleted.

        write(data):
            Write data to the interface. Subclasses should implement this method.

        read():
            Read data from the interface. Subclasses should implement this method.

        start():
            Start the interface. Subclasses should implement this method.

        stop():
            Stop the interface. Subclasses should implement this method.

        is_open() -> bool:
            Check if the interface is open and operational. Subclasses should implement this method.

    Examples:
        # Define a concrete interface class that implements InterfaceABC
        class SerialInterface(InterfaceABC):
            def __init__(self, port, baud_rate):
                # Constructor implementation here

            def write(self, data):
                # Write data implementation here

            def read(self):
                # Read data implementation here

            def start(self):
                # Start implementation here

            def stop(self):
                # Stop implementation here

            def is_open(self):
                # is_open implementation here
    """

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Constructor for the interface.

        Args:
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        pass

    def __del__(self):
        """Destructor for the interface.

        Stops the interface when the object is deleted.

        Args:
            None

        Returns:
            None
        """
        self.stop()

    @abstractmethod
    def write(self, data: bytearray):
        """Write data to the interface.

        Args:
            data: The data to be written to the interface.

        Returns:
            None
        """
        pass

    @abstractmethod
    def read(self) -> bytearray:
        """Read data from the interface.

        This method includes logic to handle framing, which may be specific to the LNet protocol.

        Returns:
            A bytearray read from the interface or None.
        """
        pass

    @abstractmethod
    def start(self):
        """Starts the interface.

        Args:
            None

        Returns:
            None
        """
        pass

    @abstractmethod
    def stop(self):
        """Stops the interface.

        Args:
            None

        Returns:
            None
        """
        pass

    @abstractmethod
    def is_open(self) -> bool:
        """Check if the interface is open and operational.

        Args:
            None

        Returns:
            bool: True if the interface is open, False otherwise.
        """
        pass
