import os
import threading
from typing import Generator, List
from contextlib import contextmanager

import pytest

from ..client.job_io.local import Connection
from ..client.job_io.local import TcpConnection
from ..client.job_io.local import FileConnection
from ..client.job_io.local import LocalWorkerProxy
from ..client.job_io.local import RemoteWorkerProxy

from ..client.job_io.remote import tcp_main
from ..client.job_io.remote import file_main


def test_single_task(communication):
    connection, _ = communication
    if connection is None:
        proxy_ctx = LocalWorkerProxy()
    else:
        proxy_ctx = RemoteWorkerProxy(connection)

    with proxy_ctx as proxy:
        assert proxy.execute(sum, ([1, 2],), None) == 3


def test_single_task_exception(communication):
    connection, _ = communication
    if connection is None:
        proxy_ctx = LocalWorkerProxy()
    else:
        proxy_ctx = RemoteWorkerProxy(connection)

    with proxy_ctx as proxy:
        with pytest.raises(TypeError):
            proxy.execute(sum, ([1, "2"],), None)


def test_max_tasks(communication):
    connection, _ = communication
    if connection is None:
        proxy_ctx = LocalWorkerProxy(max_tasks=2)
    else:
        proxy_ctx = RemoteWorkerProxy(connection, max_tasks=2)

    with proxy_ctx as proxy:
        assert proxy.execute(sum, ([1, 2],), None) == 3
        assert proxy.execute(sum, ([3, 4],), None) == 7


def test_max_tasks_exception(communication):
    connection, _ = communication
    if connection is None:
        proxy_ctx = LocalWorkerProxy(max_tasks=2)
    else:
        proxy_ctx = RemoteWorkerProxy(connection, max_tasks=2)

    with proxy_ctx as proxy:
        assert proxy.execute(sum, ([1, 2],), None) == 3
        with pytest.raises(TypeError):
            proxy.execute(sum, ([1, "2"],), None)
        with pytest.raises(RuntimeError, match="cannot send data after stopped"):
            proxy.execute(sum, ([3, 4],), None)


def test_no_max_tasks(communication):
    connection, remote = communication
    if connection is None:
        pytest.skip("test needs a remote")

    proxy_ctx = RemoteWorkerProxy(connection, max_tasks=None)

    with proxy_ctx as proxy:
        assert proxy.execute(sum, ([1, 2],), None) == 3
        remote.join(timeout=1)
        assert remote.is_alive()


def test_initializer(communication):
    global _INITIALIZED
    _INITIALIZED = None

    connection, _ = communication
    if connection is None:
        proxy_ctx = LocalWorkerProxy(initializer=_initializer, initargs=([10],))
    else:
        proxy_ctx = RemoteWorkerProxy(
            connection, initializer=_initializer, initargs=([10],)
        )

    with proxy_ctx as proxy:
        assert proxy.execute(_sum_to_initialized, ([1, 2],), None) == 13


def _initializer(value: List[int]) -> None:
    global _INITIALIZED
    try:
        if isinstance(_INITIALIZED, Exception):
            raise _INITIALIZED
    except NameError:
        pass
    _INITIALIZED = value


def _sum_to_initialized(value: List[int]) -> int:
    global _INITIALIZED  # noqa F824
    return sum(value + _INITIALIZED)


def test_initializer_exception(communication):
    global _INITIALIZED
    _INITIALIZED = RuntimeError("intentional")

    connection, _ = communication
    if connection is None:
        proxy_ctx = LocalWorkerProxy(initializer=_failing_initializer)
    else:
        proxy_ctx = RemoteWorkerProxy(connection, initializer=_failing_initializer)

    with proxy_ctx as proxy:
        with pytest.raises(RuntimeError, match="intentional"):
            proxy.initialize()
        with pytest.raises(RuntimeError, match="cannot send data after stopped"):
            proxy.execute(sum, ([1, 2],), None)


def _failing_initializer() -> None:
    raise RuntimeError("intentional")


@pytest.fixture(params=["tcp", "file", "local"])
def communication(request, tmp_path):
    if request.param == "tcp":
        with _tcp_connection() as conn:
            with _remote_tcp_env(conn):
                with _remote_job(tcp_main) as remote:
                    yield conn, remote
    elif request.param == "file":
        with _file_connection(tmp_path) as conn:
            with remote_file_env(conn):
                with _remote_job(file_main) as remote:
                    yield conn, remote
    else:
        yield None, None


@contextmanager
def _tcp_connection() -> Generator[Connection, None, None]:
    """Start the client-side TCP-based connection."""
    with TcpConnection() as conn:
        yield conn


@contextmanager
def _file_connection(tmp_path) -> Generator[Connection, None, None]:
    """Start the client-side file-based connection."""
    with FileConnection(str(tmp_path), "test") as conn:
        yield conn


@contextmanager
def _remote_tcp_env(connection: TcpConnection) -> Generator[None, None, None]:
    """Setup environment for the remote job."""
    os.environ["_PYSLURMUTILS_HOST"] = connection.host
    os.environ["_PYSLURMUTILS_PORT"] = str(connection.port)
    try:
        yield
    finally:
        del os.environ["_PYSLURMUTILS_HOST"]
        del os.environ["_PYSLURMUTILS_PORT"]


@contextmanager
def remote_file_env(connection: TcpConnection) -> Generator[None, None, None]:
    """Setup environment for the remote job."""
    os.environ["_PYSLURMUTILS_INFILE"] = connection.input_filename
    os.environ["_PYSLURMUTILS_OUTFILE"] = connection.output_filename
    try:
        yield
    finally:
        del os.environ["_PYSLURMUTILS_INFILE"]
        del os.environ["_PYSLURMUTILS_OUTFILE"]


@contextmanager
def _remote_job(remote_main: callable) -> Generator[threading.Thread, None, None]:
    """Run the remote main function in a local thread."""
    thread = threading.Thread(target=remote_main, daemon=True)
    thread.start()
    try:
        yield thread
    finally:
        thread.join(timeout=60)
        assert not thread.is_alive()
