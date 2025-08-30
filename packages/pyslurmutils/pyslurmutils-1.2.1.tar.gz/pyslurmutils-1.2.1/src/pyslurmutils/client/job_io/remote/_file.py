import os
import time
import logging

from ._base import Client
from ._base import main_task_loop
from ._base import init_job


def main():
    init_job()
    with FileClient() as client:
        main_task_loop(client)


class FileClient(Client):
    def __init__(self) -> None:
        input_filename = os.environ["_PYSLURMUTILS_INFILE"]
        output_filename = os.environ["_PYSLURMUTILS_OUTFILE"]

        logging.debug("Connecting to '%s' ...", input_filename)
        input_dirname = os.path.dirname(input_filename)
        while True:
            try:
                _ = os.listdir(input_dirname)  # force NFS cache
                self._input_file = open(input_filename, "rb+")
                break
            except FileNotFoundError:
                time.sleep(0.5)
        logging.debug("Connected to '%s'", input_filename)

        self._output_file = open(output_filename, "wb+")
        self._output_filename = output_filename

        super().__init__(input_filename, output_filename)

    def close(self) -> None:
        logging.debug("Closing connection ...")
        if self._input_file is not None:
            self._input_file.close()
            self._input_file = None
        if self._output_file is not None:
            self._output_file.close()
            self._output_file = None
        logging.debug("Connection closed")

    def _send_bytes(self, bdata):
        self._output_file.write(bdata)
        self._output_file.flush()

    def _receive_nbytes(self, nbytes):
        data = b""
        block = min(nbytes, 512)
        while len(data) < nbytes:
            data += self._input_file.read(block)
            time.sleep(0.1)
        return data
