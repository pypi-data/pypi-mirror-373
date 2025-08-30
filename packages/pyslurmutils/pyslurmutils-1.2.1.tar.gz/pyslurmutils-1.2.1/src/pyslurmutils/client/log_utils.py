import os
import time
import logging
import threading
from typing import Generator, List, Optional
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor


def monitor_log_file(
    file_path: str, stop_event: threading.Event, period: float = 0.5
) -> None:
    """Redirect a log file with the following structure to the local root logger

    .. code

        [SLURM15733578] [INFO] [root] Your log message here
        [SLURM15733578] [ERROR] [package.module] Your log message here
        ...
    """
    last_log_level = logging.INFO
    current_record = list()

    dir_name = os.path.dirname(file_path)
    while not os.path.exists(file_path) and not stop_event.is_set():
        time.sleep(period)
        _ = os.listdir(dir_name)

    if stop_event.is_set():
        return

    with open(file_path, "r") as log_file:
        while not stop_event.is_set():
            line = log_file.readline()
            if line:
                try:
                    parts = line.split(" ", 3)
                    job_id = parts[0].strip("[]")
                    level = parts[1].strip("[]")
                    name = parts[2].strip("[]")
                    message = parts[3].rstrip()

                    log_level = getattr(logging, level)
                    if not isinstance(log_level, int):
                        raise TypeError

                    if current_record:
                        logging.log(last_log_level, "\n".join(current_record))
                        current_record.clear()
                    current_record.append(f"[{job_id}] [{name}] {message}")
                    last_log_level = log_level
                except (IndexError, AttributeError, TypeError):
                    current_record.append(line.rstrip())
            else:
                time.sleep(period)


@contextmanager
def log_file_monitor_context(
    file_paths: List[Optional[str]],
) -> Generator[None, None, None]:
    """Redirect logs files to the local root logger within this context."""
    file_paths = [
        file_path for file_path in file_paths if file_path and file_path != "/dev/null"
    ]
    if not file_paths:
        yield
        return

    stop_event = threading.Event()
    with ThreadPoolExecutor(max_workers=len(file_paths)) as executor:
        futures = [
            executor.submit(monitor_log_file, file_path, stop_event)
            for file_path in file_paths
        ]
        try:
            yield
        finally:
            stop_event.set()
            for future, file_path in zip(futures, file_paths):
                try:
                    future.result()
                except Exception:
                    logging.warning("monitoring %s failed", file_path, exc_info=True)
