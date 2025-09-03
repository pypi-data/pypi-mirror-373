import logging
import threading
from abc import ABC, abstractmethod

import serial

logger = logging.getLogger(__name__)


class Transport(ABC):
    """
    Abstract base class for transport mechanisms.

    All transport implementations must define the :meth:`read` and :meth:`write` methods.
    """

    @abstractmethod
    def read(self) -> str:
        """
        Read a string from the transport.

        :return: The read string value.
        :rtype: str
        """

    @abstractmethod
    def write(self, value: str) -> None:
        """
        Write a string to the transport.

        :param value: The string to write.
        :type value: str
        """


class SerialTransport(Transport):
    """
    Serial transport implementation using the ``pyserial`` library.

    Provides thread-safe access to a serial port for reading and writing text data.

    :param port: The serial port identifier (e.g., ``/dev/ttyUSB0`` or ``COM3``).
    :type port: str
    """

    ENCODING = "utf-8"
    """Encoding used for string-byte conversion."""

    BAUDRATE = 57600

    def __init__(self, port: str, baudrate: int = BAUDRATE) -> None:
        """
        Initialize a new serial connection.

        :param port: Serial port to connect to.
        :type port: str

        :param baudrate: Baud rate. Default is 57600.
        :type baudrate: str
        """
        super().__init__()

        self._lock = threading.Lock()
        self._connection = serial.Serial(port, baudrate=baudrate, timeout=1)

    def read(self) -> str:
        """
        Read a line from the serial connection in a thread-safe manner.

        :return: Decoded string read from the serial port.
        :rtype: str
        """
        with self._lock:
            value = self._connection.readline()

        decoded_value = value.decode(self.ENCODING)
        logger.debug("read: %s", value)

        return decoded_value

    def write(self, value: str) -> None:
        """
        Write a string to the serial connection in a thread-safe manner.

        :param value: The string to send over the serial port.
        :type value: str
        """
        encoded_value = value.encode(self.ENCODING)

        with self._lock:
            logger.debug("write: %s", encoded_value)
            self._connection.write(encoded_value)
