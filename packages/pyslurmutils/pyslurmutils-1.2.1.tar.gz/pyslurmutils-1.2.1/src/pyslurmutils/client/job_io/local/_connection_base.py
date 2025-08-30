import abc
import pickle
import logging
import threading
from contextlib import contextmanager
from typing import Generator, Tuple, Any, Optional


logger = logging.getLogger(__name__)


class Connection(abc.ABC):
    """Server-side of a connection. The client-side is `ewoksjob.client.job_io.remote._base.Client`."""

    _HEADER_NBYTES = 4

    def __init__(self, raise_on_status_error: Optional[callable] = None) -> None:
        """
        :param raise_on_status_error: function that raises an exception when there is a status error (remote or local exit).
        """
        self._cancel_event = threading.Event()
        self._yield_period = 1
        self._raise_on_status_error = raise_on_status_error

    @property
    @abc.abstractmethod
    def input_name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def output_name(self) -> str:
        pass

    def __enter__(self) -> "Connection":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def cancel(self) -> None:
        self._cancel_event.set()

    def cancelled(self) -> bool:
        return self._cancel_event.is_set()

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def _wait_client(self) -> None:
        """Wait for the client to be online. The client is remote, we are the server.

        :raises RemoteExit: raises exception when not alive
        """
        pass

    @contextmanager
    def _wait_client_context(self) -> Generator[None, None, None]:
        logger.debug("waiting for remote job to connect to %s ...", self.output_name)
        try:
            yield
        except Exception:
            logger.debug(
                "waiting for remote job to connect to %s failed", self.output_name
            )
            raise
        if self.cancelled():
            logger.debug(
                "waiting for remote job to connect to %s cancelled", self.output_name
            )
        else:
            logger.debug("remote job connected to %s", self.output_name)

    def send_data(self, data: Any) -> None:
        bdata = self._serialize_data(data)
        nbytes = len(bdata)
        logger.debug(
            "send data %s (%d bytes) to client of %s ...",
            type(data),
            nbytes,
            self.output_name,
        )
        bheader = self._serialize_header(bdata)
        try:
            self._send_bytes_with_check(bheader + bdata)
        except (BrokenPipeError, ConnectionResetError):
            if data is None:
                logger.debug("client of %s already exited", self.output_name)
                return
            raise
        logger.debug("data send to client of %s", self.output_name)

    def receive_data(self) -> Tuple[Any, Optional[BaseException]]:
        logger.debug("waiting for client data on %s ...", self.input_name)
        bheader = self._receive_nbytes_with_check(self._HEADER_NBYTES)
        nbytes = self._deserialize_header(bheader)
        if nbytes == 0:
            logger.warning(
                "corrupt header %s from client on %s ...", bheader, self.input_name
            )
        bdata = self._receive_nbytes_with_check(nbytes)
        logger.debug("client data received from %s", self.input_name)
        return self._deserialize_data(bdata)

    def _serialize_header(self, bdata: bytes) -> bytes:
        return len(bdata).to_bytes(self._HEADER_NBYTES, "big")

    def _deserialize_header(self, bheader: bytes) -> int:
        return int.from_bytes(bheader, "big")

    def _serialize_data(self, data: Any) -> bytes:
        return pickle.dumps(data)

    def _deserialize_data(self, data: bytes) -> Any:
        return pickle.loads(data)

    def _receive_nbytes_with_check(self, nbytes: int) -> bytes:
        """
        :raises RemoteExit: raises exception when not alive
        :raises ValueError: rcancelled or did not receive the requested number of bytes
        """
        bdata = self._receive_nbytes(nbytes)
        if len(bdata) != nbytes:
            err_msg = f"{len(bdata)} bytes received from {self.input_name} instead of {nbytes} bytes"
            if self.cancelled():
                raise ValueError(f"{err_msg} (cancelled)")
            else:
                raise ValueError(err_msg)
        return bdata

    @abc.abstractmethod
    def _receive_nbytes(self, nbytes: int) -> bytes:
        """
        :raises RemoteExit: raises exception when not alive
        """
        pass

    def _send_bytes_with_check(self, data: bytes) -> None:
        """
        :raises RuntimeError: rcancelled
        """
        if self.cancelled():
            raise RuntimeError(f"send to %{self} is cancelled")
        self._send_bytes(data)

    @abc.abstractmethod
    def _send_bytes(self, data: bytes) -> None:
        pass


class Buffer:
    def __init__(self, nbytes: int) -> None:
        self.data = b""
        self._nbytes = nbytes
        self._max_chunk_size = min(nbytes, 512)

    @property
    def chunk_size(self) -> int:
        return min(self._max_chunk_size, self._nbytes - len(self.data))
