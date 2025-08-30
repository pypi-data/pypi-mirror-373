import os
import time
import logging
import warnings
from uuid import uuid4
from typing import Optional

from ... import os_utils
from ...errors import RemoteExit
from ._connection_base import Buffer
from ._connection_base import Connection

logger = logging.getLogger(__name__)


class FileConnection(Connection):
    def __init__(
        self,
        directory: str,
        basename: str,
        raise_on_status_error: Optional[callable] = None,
    ) -> None:
        conn_id = str(uuid4())
        os_utils.makedirs(directory)
        input_filename = os.path.join(directory, f"{basename}.in.{conn_id}.pkl")
        output_filename = os.path.join(directory, f"{basename}.out.{conn_id}.pkl")

        self._input_filename = input_filename
        self._output_filename = output_filename
        self._output_file = None
        self._input_file = open(input_filename, "wb+")
        self._timout_after_remote_exit = 10

        logger.debug("start writing %s", input_filename)
        super().__init__(raise_on_status_error=raise_on_status_error)

    @property
    def input_name(self) -> str:
        return self._output_filename

    @property
    def output_name(self) -> str:
        return self._input_filename

    @property
    def input_filename(self) -> str:
        return self._input_filename

    @property
    def output_filename(self) -> str:
        return self._output_filename

    def close(self):
        if self._input_file is not None:
            self._input_file.close()
            self._input_file = None
            _delete_file_with_retry(self._input_filename)
        if self._output_file is not None:
            self._output_file.close()
            self._output_file = None
            _delete_file_with_retry(self._output_filename)

    def _wait_client(self) -> None:
        """
        :raises RemoteExit: raises exception when not alive
        """
        if self._output_file is not None:
            return
        with self._wait_client_context():
            remote_checker = _RemoteChecker(
                self._timout_after_remote_exit, self._raise_on_status_error
            )
            while not self.cancelled():
                try:
                    self._nfs_cache_refresh()
                    self._output_file = open(self._output_filename, "rb+")
                    break
                except FileNotFoundError:
                    pass

                time.sleep(self._yield_period)

                remote_checker.raise_on_status_error()

    def _send_bytes(self, data: bytes) -> None:
        self._input_file.write(data)
        self._input_file.flush()

    def _receive_nbytes(self, nbytes: int) -> bytes:
        """
        :raises RemoteExit: raises exception when not alive
        """
        buffer = Buffer(nbytes)
        remote_checker = _RemoteChecker(
            self._timout_after_remote_exit, self._raise_on_status_error
        )

        while not self.cancelled() and len(buffer.data) < nbytes:
            if self._output_file is None:
                self._wait_client()
            self._reopen_output_file()
            buffer.data += self._output_file.read(buffer.chunk_size)
            if len(buffer.data) >= nbytes:
                break
            time.sleep(self._yield_period)
            remote_checker.raise_on_status_error()

        return buffer.data

    def _reopen_output_file(self):
        if self._output_file is None:
            return
        pos = self._output_file.tell()
        self._output_file.close()
        self._nfs_cache_refresh()
        self._output_file = open(self._output_filename, "rb+")
        self._output_file.seek(pos)

    def _nfs_cache_refresh(self):
        dirname = os.path.dirname(self._output_filename)
        return os_utils.nfs_cache_refresh(dirname)


class _RemoteChecker:
    def __init__(
        self,
        timout_after_remote_exit: float,
        raise_on_status_error: Optional[callable] = None,
    ):
        self._timout_after_remote_exit = timout_after_remote_exit
        self._raise_on_status_error = raise_on_status_error
        self._remote_exit = None
        self._t0_remote_exit = None

    def raise_on_status_error(self) -> None:
        """
        :raises RemoteExit: status error (remote or local exit).
        """
        if self._t0_remote_exit:
            if (time.time() - self._t0_remote_exit) > self._timout_after_remote_exit:
                raise self._remote_exit
        elif self._raise_on_status_error:
            try:
                self._raise_on_status_error()
            except RemoteExit as ex:
                logger.debug(
                    "%s; try reading connection file for %.1f sec",
                    ex,
                    self._timout_after_remote_exit,
                )
                self._remote_exit = ex
                self._t0_remote_exit = time.time()


def _delete_file_with_retry(
    filename: str,
    max_attempts: int = 5,
    initial_delay: float = 0.1,
    max_delay: float = 1,
) -> None:
    delay = initial_delay / 2
    for _ in range(max_attempts):
        try:
            os.remove(filename)
            return
        except PermissionError:
            delay = min(delay * 2, max_delay)
            time.sleep(delay)
    warnings.warn(f"Could not remove file {filename}", UserWarning, stacklevel=2)
