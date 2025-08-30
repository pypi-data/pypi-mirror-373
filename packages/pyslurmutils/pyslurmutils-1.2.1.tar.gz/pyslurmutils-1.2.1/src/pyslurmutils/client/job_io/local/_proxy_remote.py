import logging
from typing import Any, Optional, Tuple

from ._connection_base import Connection
from ._connection_file import FileConnection
from ._connection_tcp import TcpConnection
from ._proxy_base import WorkerProxy
from ..remote import remote_script

logger = logging.getLogger(__name__)


class RemoteWorkerProxy(WorkerProxy):
    """Worker proxy which executes tasks remotely over a :code:`Connection`."""

    def __init__(
        self,
        connection: Connection,
        initializer: Optional[callable] = None,
        initargs: Optional[tuple] = None,
        initkwargs: Optional[tuple] = None,
        max_tasks: Optional[int] = None,
    ) -> None:
        self._connection = connection

        if isinstance(connection, FileConnection):
            self._remote_environment = {
                "_PYSLURMUTILS_INFILE": connection.input_filename,
                "_PYSLURMUTILS_OUTFILE": connection.output_filename,
            }
            self._metadata = {
                "connection": "file",
                "infile": connection.input_filename,
                "outfile": connection.output_filename,
            }
        elif isinstance(connection, TcpConnection):
            self._remote_environment = {
                "_PYSLURMUTILS_HOST": connection.host,
                "_PYSLURMUTILS_PORT": connection.port,
            }
            self._metadata = {"connection": "tcp"}
        else:
            raise TypeError(connection)

        super().__init__(
            initializer=initializer,
            initargs=initargs,
            initkwargs=initkwargs,
            max_tasks=max_tasks,
        )

    def remote_script(self) -> str:
        return remote_script(self._metadata["connection"])

    @property
    def remote_environment(self) -> dict:
        return self._remote_environment

    @property
    def metadata(self) -> dict:
        return self._metadata

    def _send(self, data: Any) -> None:
        self._connection.send_data(data)

    def _get_result(self) -> Tuple[Any, Optional[BaseException]]:
        return self._connection.receive_data()
