"""
tcp_client.py
Written by: Joshua Kitchen - 2024
"""
import logging
import socket
from typing import Generator

from .utils import encode_msg, decode_header, vet_address

logger = logging.getLogger(__name__)


class TCPClient:
    """
    A TCP client that can connect to or host a TCP connection.
    """

    def __init__(self, timeout: int | float | None = None, is_component=False):
        self._soc = None
        self._listen_soc = None
        self._peer_addr = None
        self._local_addr = None
        self._timeout = timeout
        self._is_connected = False
        self._is_host = False
        self._last_connected_peer = (None, None)

        # Indicates that TCPClient is a member of another class, specifically a ClientProcessor. This will supress log
        # messages in _handle_error(), receive_bytes(), send_bytes(), and disconnect(), since ClientProcessor
        # already has its own logging for these functions
        self._is_component = is_component

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __repr__(self):
        return (f"<TCPClient local_addr={self._local_addr} "
                f"peer_addr={self._peer_addr} "
                f"is_connected={self.is_connected} "
                f"is_host={self.is_host}>")

    @classmethod
    def from_socket(cls, soc: socket.socket, is_listen_soc=False, is_component=False) -> "TCPClient":
        """
        Creates a client from an existing socket object. The timeout value for the socket is overridden when
        connect() or host_single_client() is called to ensure class consistency. Returns a new TCPClient object.
        NOTE: if bind() or listen() is called on the socket before host_single_client() or connect() is called,
        both methods will raise an exception.
        """
        out = cls(soc.gettimeout())
        if is_listen_soc:
            out._listen_soc = soc
            out._is_host = True
            return out
        else:
            out._soc = soc
        try:
            out._peer_addr = soc.getpeername()
            out._local_addr = soc.getsockname()
        except OSError:  # Not connected
            return out
        out._last_connected_peer = out._peer_addr
        out._is_connected = True
        out._is_component = is_component
        return out

    def _clean_up(self):
        if self._soc is not None:
            try:
                self._soc.close()
            except OSError:
                logger.exception("Error when trying to close socket")
            finally:
                self._soc = None

        if self._listen_soc is not None:
            try:
                self._listen_soc.close()
            except OSError:
                logger.exception("Error when trying to close listening socket")
            finally:
                self._listen_soc = None

        self._peer_addr = None
        self._local_addr = None
        self._is_connected = False
        self._is_host = False

    def _handle_error(self, exception: Exception, log_msg: str, *log_args):
        if not self._is_component:
            logger.error(log_msg, *log_args)
        self._clean_up()
        raise exception.__class__(log_msg % log_args)

    @property
    def is_connected(self) -> bool:
        """Indicates whether the client is currently connected. Read-only."""
        return self._is_connected

    @property
    def timeout(self) -> int | float | None:
        """Timeout (in seconds) for socket operations. A value of `None` indicates an infinite timeout."""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: int | float | None):
        """
        Sets the timeout (in seconds) of the client. The Timeout argument should be a positive integer.
        A value of `None` disables timeouts.
        """
        if timeout is not None:
            if timeout < 0:
                raise ValueError("Value for timeout should be a positive integer")
        self._timeout = timeout
        if self._soc:
            self._soc.settimeout(self._timeout)

    @property
    def local_addr(self) -> tuple[str, int] | None:
        """
        The address of this client object. If the client is hosting, this is the address
        that was bound to. Returns 'None' if not connected.
        """
        return self._local_addr

    @property
    def peer_addr(self) -> tuple[str, int] | None:
        """
        Address of the remote host. Returns `None` if disconnected.
        """
        return self._peer_addr

    @property
    def is_host(self) -> bool:
        """
        `True` if the client is acting as a host, otherwise `False`.
        """
        return self._is_host

    def host_single_client(self, addr: tuple[str, int], timeout: int | float | None = None):
        """
        Hosts a single connection from a remote TCP client. The timeout argument sets how long this
        method will listen for a connection; 'None' indicates an infinite timeout (default).
        """
        if self._is_connected:
            return

        if not vet_address(addr):
            raise ValueError(f"{addr} is an invalid ipv4 address")
        if addr[0] == "255.255.255.255":
            raise ValueError("Cannot connect to '255.255.255.255' (broadcast address)")

        if not self._listen_soc:
            self._listen_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._listen_soc.settimeout(timeout)
        self._local_addr = addr
        try:
            self._listen_soc.bind(self._local_addr)
        except socket.gaierror as e:
            self._handle_error(e, "Could not resolve address %s @ %d", self._local_addr[0], self._local_addr[1])
        except OSError as e:
            self._handle_error(e, "Exception while binding to %s @ %d", self._local_addr[0], self._local_addr[1])

        logger.info("Listening for connections on %s @ %d", self._local_addr[0], self._local_addr[1])
        try:
            self._listen_soc.listen()
            client_soc, client_addr = self._listen_soc.accept()
        except TimeoutError as e:
            self._handle_error(e, "Timed out while attempting to connect to remote client")
        except ConnectionError as e:
            self._handle_error(e, "Failed to establish connection to remote client")

        self._soc = client_soc
        self._peer_addr = client_addr
        self._last_connected_peer = self._peer_addr
        self._is_connected = True
        self._is_host = True
        logger.info("Accepted connection from %s @ %d", client_addr[0], client_addr[1])
        self._listen_soc.close()
        self._listen_soc = None
        return

    def connect(self, addr: tuple[str, int]):
        """
        Connects to a remote TCP host.
        """
        if self._is_connected:
            return

        if not self._soc:
            if not vet_address(addr):
                raise ValueError(f"{addr} is an invalid ipv4 address")
            if addr[0] == "0.0.0.0":
                raise ValueError("Cannot connect to '0.0.0.0' (unspecified address)")
            if addr[0] == "255.255.255.255":
                raise ValueError("Cannot connect to '255.255.255.255' (broadcast address)")
            self._soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._soc.settimeout(self._timeout)
        self._peer_addr = addr
        self._last_connected_peer = addr

        logger.info("Attempting to connect to %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])
        try:
            self._soc.connect(self._peer_addr)
        except TimeoutError as e:
            self._handle_error(e, "Timed out while attempting to connect to %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])
        except ConnectionError as e:
            self._handle_error(e, "Could not connect to %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])
        except socket.gaierror as e:
            self._handle_error(e, "Could not resolve address %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])
        except OSError as e:
            self._handle_error(e, "OSError while connecting to %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])

        self._is_connected = True
        self._is_host = False
        self._local_addr = self._soc.getsockname()
        logger.info("Successfully connected to %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])

    def reconnect(self):
        """
        Attempts to reconnect to the last successfully connected peer.
        """
        if not self._last_connected_peer[0] or not self._last_connected_peer[1]:
            raise ConnectionError("No previous connection available to reconnect to")

        self.disconnect()
        try:
            self.connect(self._last_connected_peer)
        except (TimeoutError, ConnectionError, OSError, socket.gaierror) as e:
            self._handle_error(e, "Reconnect attempt to %s @ %d failed", self._last_connected_peer[0], self._last_connected_peer[1])

    def disconnect(self):
        """
        Gracefully disconnects from the remote host. If no connection is opened, this method does nothing.
        """
        if self._is_connected:
            self._clean_up()
            if not self._is_component:
                logger.info("Disconnected from %s @ %d",                                                                                                                     self._last_connected_peer[0], self._last_connected_peer[1])

    def send_raw(self, data: bytes) -> bool:
        """
        Send data with no size header.
        """
        if not self._is_connected:
            raise ConnectionError("Client is not connected to a host")
        try:
            self._soc.sendall(data)
        except AttributeError: # Socket was closed from another thread
            self._clean_up()
            return False
        except TimeoutError as e:
            if not self._is_component:
                logger.warning("Timed out while sending from %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])
            raise e
        except ConnectionError as e:
            self._handle_error(e, "Connection error while sending to %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])
        except OSError as e:
            self._handle_error(e, "OSError while sending to %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])
        return True

    def send(self, data: bytes) -> bool:
        """
        Send data with a 4 byte size header.
        """
        if not self._is_connected:
            raise ConnectionError("Client is not connected to a host")
        return self.send_raw(encode_msg(data))

    def receive_raw(self, size: int) -> bytes:
        """
        Receives exactly `size` bytes. Returns an empty bytes object on connection closure.
        """
        if not self.is_connected:
            raise ConnectionError("Client is not connected to a host")
        if size <= 0:
            raise ValueError("'size' argument must be a non-zero, positive integer")
        try:
            data = self._soc.recv(size)
        except AttributeError: # Socket was closed from another thread
            self._clean_up()
            return bytes(0)
        except TimeoutError as e:
            if not self._is_component:
                logger.warning("Timed out while receiving from %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])
            raise e
        except ConnectionError as e:
            self._handle_error(e, "Connection error while receiving from %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])
        except OSError as e:
            self._handle_error(e, "OSError while receiving from %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])

        return data


    def iter_receive(self, buff_size: int = 4096) -> Generator:
        """
        Generator that yields chunks of a message. First yield is the total message size.
        This method expects a 4 bytes size header to be attached.
        """
        if not self._is_connected:
            raise ConnectionError("Client is not connected to a host")
        if buff_size <= 0:
            raise ValueError("'buff_size' argument must be a non-zero, positive integer")
        bytes_recv = 0
        header = self.receive_raw(4)
        if not header:
            return
        if len(header) < 4:
            logger.warning("Incomplete header from %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])
            return
        size = decode_header(header)
        logger.debug("Incoming message from %s @ %d, SIZE=%d",
                     self._last_connected_peer[0], self._last_connected_peer[1], size)
        yield size
        if size < buff_size:
            buff_size = size
        while bytes_recv < size:
            data = self.receive_raw(buff_size)
            if not data:
                logger.debug("Failed to complete reception of message from %s @ %d. %d/%d bytes received",
                             self._last_connected_peer[0], self._last_connected_peer[1], bytes_recv, size)
                return
            bytes_recv += len(data)
            remaining = size - bytes_recv
            if remaining < buff_size:
                buff_size = remaining
            yield data

    def receive(self, buff_size: int = 4096, suppress_logs=False) -> bytearray:
        """
        Receives a full message as a bytearray. This method expects a 4 bytes size header to be attached.
        Returns empty bytearray on failure or closed connection. This method expects a 4 bytes size header to be attached.
        """
        if not self._is_connected:
            raise ConnectionError("Client is not connected to a host")
        if buff_size <= 0:
            raise ValueError("'buff_size' argument must be a non-zero, positive integer")
        gen = self.iter_receive(buff_size)
        if not gen:
            return bytearray()
        try:
            next(gen) # Size is always yielded first, but we won't need it in this method
        except StopIteration:
            return bytearray()
        data = bytearray()
        for chunk in gen:
            if not chunk:
                logger.warning("Partial message received from %s @ %d", self._last_connected_peer[0], self._last_connected_peer[1])
                return data
            data.extend(chunk)
        logger.debug("Received a total of %d bytes from %s @ %d", len(data), self._last_connected_peer[0], self._last_connected_peer[1])
        return data
