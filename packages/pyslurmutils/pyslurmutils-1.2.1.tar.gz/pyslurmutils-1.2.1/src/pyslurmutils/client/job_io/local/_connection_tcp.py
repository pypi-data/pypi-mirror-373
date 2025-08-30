import time
import random
import socket
import logging
from functools import lru_cache
from typing import Optional

from ... import defaults
from ._connection_base import Buffer
from ._connection_base import Connection

logger = logging.getLogger(__name__)


class TcpConnection(Connection):
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        min_port: Optional[int] = None,
        num_ports: Optional[int] = None,
        raise_on_status_error: Optional[callable] = None,
    ) -> None:
        if host is None:
            host = get_host()
        if port is None:
            self._server_sock = lock_port(host, min_port=min_port, num_ports=num_ports)
        else:
            self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_sock.bind((host, port))
        port = self._server_sock.getsockname()[-1]

        self._host = host
        self._port = port
        self._hostport = f"{host}:{port}"

        self._client_socket = None

        self._server_sock.listen(1)
        self._server_sock.settimeout(0.5)

        logger.debug("start listening on %s:%s", host, port)
        super().__init__(raise_on_status_error=raise_on_status_error)

    @property
    def input_name(self) -> str:
        return self._hostport

    @property
    def output_name(self) -> str:
        return self._hostport

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> str:
        return self._port

    def close(self):
        if self._client_socket:
            self._client_socket.close()
        self._server_sock.close()

    def _wait_client(self) -> None:
        """
        :raises RemoteExit: raises exception when not alive
        """
        if self._client_socket is not None:
            return
        with self._wait_client_context():
            while not self.cancelled():
                try:
                    self._client_socket, _ = self._server_sock.accept()
                    self._client_socket.settimeout(1)
                    break
                except socket.timeout:
                    pass

                time.sleep(self._yield_period)

                if self._raise_on_status_error:
                    self._raise_on_status_error()

    def _send_bytes(self, data: bytes) -> None:
        if self._client_socket is None:
            self._wait_client()
        self._client_socket.sendall(data)

    def _receive_nbytes(self, nbytes: int) -> bytes:
        """
        :raises RemoteExit: raises exception when not alive
        """
        buffer = Buffer(nbytes)

        while not self.cancelled() and len(buffer.data) < nbytes:
            if self._client_socket is None:
                self._wait_client()

            try:
                data = self._client_socket.recv(buffer.chunk_size)
            except socket.timeout:
                pass
            else:
                if not data:
                    raise RuntimeError("Remote job shutdown")
                buffer.data += data
                if len(buffer.data) >= nbytes:
                    break

            time.sleep(self._yield_period)

            if self._raise_on_status_error:
                try:
                    self._raise_on_status_error()
                except Exception:
                    self._fetch_pending_data(buffer)
                    if len(buffer.data) >= nbytes:
                        break
                    raise

        return buffer.data

    def _fetch_pending_data(self, buffer: Buffer):
        try:
            data = self._client_socket.recv(buffer.chunk_size)
            while data:
                buffer.data += data
                data = self._client_socket.recv(buffer.chunk_size)
        except Exception:
            pass


@lru_cache(1)
def get_host() -> str:
    return socket.gethostbyname(socket.gethostname())


def lock_port(
    host: str, min_port: Optional[int] = None, num_ports: Optional[int] = None
) -> int:
    if min_port is None:
        min_port = defaults.MIN_PORT
    if num_ports is None:
        num_ports = defaults.NUM_PORTS
    preferred_ports = list(range(min_port, min_port + num_ports + 1))
    random.shuffle(preferred_ports)

    # Find a free port in the preferred range
    for port in preferred_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((host, port))
            return sock
        except Exception:
            sock.close()
        except BaseException:
            sock.close()
            raise

    # Preferred ports are already in use, find any free port.
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((host, 0))
            return sock
        except Exception:
            sock.close()
        except BaseException:
            sock.close()
            raise
