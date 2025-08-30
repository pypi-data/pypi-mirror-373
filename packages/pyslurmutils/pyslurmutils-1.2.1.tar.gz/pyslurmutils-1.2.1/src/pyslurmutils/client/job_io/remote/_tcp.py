import os
import time
import socket
import logging

from ._base import Client
from ._base import main_task_loop
from ._base import init_job


def main():
    init_job()
    with TcpClient() as client:
        main_task_loop(client)


class TcpClient(Client):
    def __init__(self) -> None:
        host = os.environ.get("_PYSLURMUTILS_HOST")
        port = int(os.environ.get("_PYSLURMUTILS_PORT"))
        try:
            hostname = socket.gethostbyaddr(host)[0]
        except Exception:
            hostname = host
        remote_name = f"{hostname}:{port}"

        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.debug("Connecting to %s ...", remote_name)
        self._client_socket.settimeout(10)
        self._client_socket.connect((host, port))
        logging.debug("Connected to %s", remote_name)
        self._client_socket.settimeout(None)

        super().__init__(remote_name, remote_name)

    def close(self) -> None:
        logging.debug("Closing connection ...")
        try:
            self._client_socket.shutdown(socket.SHUT_WR)
        except Exception:
            pass
        self._client_socket.close()
        logging.debug("Connection closed")

    def _send_bytes(self, bdata):
        self._client_socket.sendall(bdata)

    def _receive_nbytes(self, nbytes):
        data = b""
        block = min(nbytes, 512)
        while len(data) < nbytes:
            data += self._client_socket.recv(block)
            time.sleep(0.1)
        return data
