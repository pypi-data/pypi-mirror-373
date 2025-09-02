"""
This module defines base classes and generic functions to work with sockets.
"""

import socket

from egse.device import DeviceConnectionError
from egse.device import DeviceConnectionInterface
from egse.device import DeviceTimeoutError
from egse.device import DeviceTransport
from egse.log import logger


class SocketDevice(DeviceConnectionInterface, DeviceTransport):
    """Base class that implements the socket interface."""

    def __init__(self, hostname: str, port: int):
        super().__init__()
        self.is_connection_open = False
        self.hostname = hostname
        self.port = port
        self.socket = None

    @property
    def device_name(self):
        """The name of the device that this interface connects to."""
        raise NotImplementedError

    def connect(self):
        """
        Connect the device.

        Raises:
            ConnectionError: When the connection could not be established. Check the logging
                messages for more detail.
            TimeoutError: When the connection timed out.
            ValueError: When hostname or port number are not provided.
        """

        # Sanity checks

        if self.is_connection_open:
            logger.warning(f"{self.device_name}: trying to connect to an already connected socket.")
            return

        if self.hostname in (None, ""):
            raise ValueError(f"{self.device_name}: hostname is not initialized.")

        if self.port in (None, 0):
            raise ValueError(f"{self.device_name}: port number is not initialized.")

        # Create a new socket instance

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e_socket:
            raise ConnectionError(f"{self.device_name}: Failed to create socket.") from e_socket

        # We set a timeout of 3 sec before connecting and reset to None
        # (=blocking) after the connect. The reason for this is because when no
        # device is available, e.g during testing, the timeout will take about
        # two minutes which is way too long. It needs to be evaluated if this
        # approach is acceptable and not causing problems during production.

        try:
            logger.debug(f'Connecting a socket to host "{self.hostname}" using port {self.port}')
            self.socket.settimeout(3)
            self.socket.connect((self.hostname, self.port))
            self.socket.settimeout(None)
        except ConnectionRefusedError as exc:
            raise ConnectionError(f"{self.device_name}: Connection refused to {self.hostname}:{self.port}.") from exc
        except TimeoutError as exc:
            raise TimeoutError(f"{self.device_name}: Connection to {self.hostname}:{self.port} timed out.") from exc
        except socket.gaierror as exc:
            raise ConnectionError(f"{self.device_name}: socket address info error for {self.hostname}") from exc
        except socket.herror as exc:
            raise ConnectionError(f"{self.device_name}: socket host address error for {self.hostname}") from exc
        except socket.timeout as exc:
            raise TimeoutError(f"{self.device_name}: socket timeout error for {self.hostname}:{self.port}") from exc
        except OSError as exc:
            raise ConnectionError(f"{self.device_name}: OSError caught ({exc}).") from exc

        self.is_connection_open = True

    def disconnect(self):
        """
        Disconnect from the Ethernet connection.

        Raises:
            ConnectionError when the socket could not be closed.
        """

        try:
            if self.is_connection_open:
                logger.debug(f"Disconnecting from {self.hostname}")
                self.socket.close()
                self.is_connection_open = False
        except Exception as e_exc:
            raise ConnectionError(f"{self.device_name}: Could not close socket to {self.hostname}") from e_exc

    def is_connected(self) -> bool:
        """
        Check if the device is connected.

        Returns:
             True is the device is connected, False otherwise.
        """

        return bool(self.is_connection_open)

    def reconnect(self):
        """
        Reconnect to the device. If the connection is open, this function will first disconnect
        and then connect again.
        """

        if self.is_connection_open:
            self.disconnect()
        self.connect()

    def read(self) -> bytes:
        """

        Returns:
            A bytes object containing the received telemetry.
        """
        idx, n_total = 0, 0
        buf_size = 1024 * 4
        response = bytes()

        try:
            for idx in range(100):
                # time.sleep(0.1)  # Give the device time to fill the buffer
                data = self.socket.recv(buf_size)
                n = len(data)
                n_total += n
                response += data
                # if n < buf_size:
                #     break  # there is not more data in the buffer
                if b"\x03" in response:
                    break
        except socket.timeout as e_timeout:
            logger.warning(f"Socket timeout error from {e_timeout}")
            raise DeviceTimeoutError(self.device_name, "Socket timeout error") from e_timeout

        # logger.debug(f"Total number of bytes received is {n_total}, idx={idx}")

        return response

    def write(self, command: str):
        """
        Send a command to the device.

        No processing is done on the command string, except for the encoding into a bytes object.

        Args:
            command: the command string including terminators.

        Raises:
            A DeviceTimeoutError when the send timed out, and a DeviceConnectionError if
            there was a socket related error.
        """

        try:
            self.socket.sendall(command.encode())
        except socket.timeout as e_timeout:
            raise DeviceTimeoutError(self.device_name, "Socket timeout error") from e_timeout
        except socket.error as e_socket:
            # Interpret any socket-related error as an I/O error
            raise DeviceConnectionError(self.device_name, "Socket communication error.") from e_socket

    def trans(self, command: str) -> bytes:
        """
        Send a command to the device and wait for the response.

        No processing is done on the command string, except for the encoding into a bytes object.

        Args:
            command: the command string including terminators.

        Returns:
            A bytes object containing the response from the device. No processing is done
            on the response.

        Raises:
            A DeviceTimeoutError when the send timed out, and a DeviceConnectionError if
            there was a socket related error.
        """

        try:
            # Attempt to send the complete command

            self.socket.sendall(command.encode())

            # wait for, read and return the response (will be at most TBD chars)

            return_string = self.read()

            return return_string

        except socket.timeout as e_timeout:
            raise DeviceTimeoutError(self.device_name, "Socket timeout error") from e_timeout
        except socket.error as e_socket:
            # Interpret any socket-related error as an I/O error
            raise DeviceConnectionError(self.device_name, "Socket communication error.") from e_socket
