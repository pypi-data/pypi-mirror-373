import queue
import weakref
import logging
import threading
from concurrent import futures
from contextlib import contextmanager
from typing import Optional, Callable, Set, Generator, Any, Tuple

from ... import errors

logger = logging.getLogger(__name__)

ExecuteType = Callable[[callable, tuple, dict, futures.Future], Any]
WorkerExitMessageType = Callable[[], str]
ExecuteContextReturnType = Generator[
    Tuple[ExecuteType, WorkerExitMessageType], None, None
]


class ExecutorShutdown(Exception):
    pass


class RemoteExecutor(futures.Executor):
    """Asynchronous executor which delegates task execution to :math:`WorkerProxy` instances."""

    _FUTURE_CLASS = futures.Future

    def __init__(
        self,
        max_workers: Optional[int] = None,
        max_tasks_per_worker: Optional[int] = None,
        lazy_scheduling: bool = True,
        conservative_scheduling: bool = False,
    ):
        """
        :param max_workers: maximum number of workers that can run at any given time. `None` means unlimited.
        :param max_tasks_per_worker: maximum number of tasks each worker can receive before exiting. `None` means unlimited.
        :param lazy_scheduling: schedule workers only when needed. Can only be disabled when `max_workers` is specified.
        :param conservative_scheduling: schedule the least amount of workers at the expense of tasks staying longer in the queue.
        """
        if max_workers is None:
            if not lazy_scheduling:
                raise ValueError(
                    "Cannot disable lazy scheduling when there is no maximum number of workers"
                )
        else:
            if not isinstance(max_workers, int):
                raise TypeError("max_workers must be an integer")
            elif max_workers <= 0:
                raise ValueError("max_workers must be greater than 0")
        self._max_workers = max_workers

        if max_tasks_per_worker is not None:
            if not isinstance(max_tasks_per_worker, int):
                raise TypeError("max_tasks_per_worker must be an integer")
            elif max_tasks_per_worker <= 0:
                raise ValueError("max_tasks_per_worker must be >= 1")
        self._max_tasks_per_worker = max_tasks_per_worker

        self._lazy_scheduling = lazy_scheduling
        self._task_queue = queue.Queue()
        self._shutdown_lock = threading.Lock()
        self._workers: Set[threading.Thread] = set()
        self._futures = weakref.WeakSet()
        self._shutdown_flag = False
        self._conservative_scheduling = conservative_scheduling

        if not lazy_scheduling:
            for _ in range(self._max_workers):
                self._start_worker()

    def submit(self, task: Callable, *args, **kwargs) -> futures.Future:
        """
        :param task: function to be executed remotely
        :param args: positional arguments of the function to be executed remotely
        :param kwargs: named arguments of the function to be executed remotely
        :returns: future object to retrieve the result
        """
        with self._shutdown_lock:
            if self._shutdown_flag:
                raise RuntimeError("ThreadPool has been shut down")

            future = self._FUTURE_CLASS()
            # self._futures.add(future)
            self._task_queue.put((task, args, kwargs, future))
            logger.debug(
                "%s: submitted (task capacity = %s)",
                type(self).__name__,
                self._task_capacity(),
            )

            if self._lazy_scheduling and self._require_more_workers():
                self._start_worker()
        return future

    def shutdown(self, wait: bool = True, cancel: bool = False):
        """
        :param wait: wait for all workers to exit
        :param cancel: cancel all pending tasks (running once cannot be cancelled)
        """
        with self._shutdown_lock:
            self._shutdown_flag = True
            workers = list(self._workers)

            if cancel:
                for future in list(self._futures):
                    future.cancel()

            # Sentinel to shut down workers
            for _ in range(len(workers)):
                self._task_queue.put((None, None, None, None))

        if wait:
            for worker in workers:
                worker.join()
        self._workers.clear()

    def _task_capacity(self) -> int:
        """The total number of tasks that the running workers can execute."""
        return sum(worker.task_capacity for worker in self._workers)

    def _idle_workers(self) -> int:
        """The total number of idle workers"""
        return sum(worker.idle for worker in self._workers)

    def _max_task_queue_size(self) -> int:
        if self._conservative_scheduling:
            return self._task_capacity()
        else:
            return self._idle_workers()

    def _require_more_workers(self) -> bool:
        if self._shutdown_flag:
            # Do not start workers when shutting down
            return False
        if self._max_workers and len(self._workers) >= self._max_workers:
            # Already the maximum amount of workers
            return False
        if self._task_queue.qsize() <= self._max_task_queue_size():
            # Workers have enough capacity to drain the task queue
            return False
        return True

    def _start_worker(self) -> None:
        if self._shutdown_flag:
            # Do not start workers when shutting down
            return False
        thread_name = f"{type(self).__name__}-{len(self._workers)}"
        task_capacity = self._max_tasks_per_worker or float("inf")
        worker = threading.Thread(
            target=self._worker_main,
            name=thread_name,
            daemon=True,
        )
        worker.task_capacity = task_capacity
        worker.idle = False
        worker.start()
        self._workers.add(worker)
        return True

    def _worker_main(self):
        worker = threading.current_thread()
        logger.debug(
            "%s: started (task capacity = %s)", worker.name, worker.task_capacity
        )
        exit_reason = "cancelled"
        try:
            with self.execute_context() as (execute, worker_exit_msg):
                while not self._shutdown_flag:
                    try:
                        worker.idle = True
                        task, args, kwargs, future = self._task_queue.get(timeout=1)
                    except queue.Empty:
                        exit_msg = worker_exit_msg()
                        if exit_msg:
                            exit_reason = exit_msg
                            break
                        continue

                    try:
                        worker.idle = False

                        if task is None:  # Sentinel to shut down the worker
                            exit_reason = "requested to stop"
                            break

                        worker.task_capacity -= 1
                        if future.set_running_or_notify_cancel():
                            logger.info(
                                "%s: execute %s (task capacity = %s)",
                                worker.name,
                                task,
                                worker.task_capacity,
                            )
                            try:
                                result = execute(task, args, kwargs, future)
                            except Exception as exc:
                                future.set_exception(exc)
                                # self = None  # TODO: break a reference cycle with the exception 'exc' but we need self later
                                if isinstance(
                                    exc, (ExecutorShutdown, errors.RemoteExit)
                                ):
                                    exit_reason = str(exc)
                                    logger.info(
                                        "%s: %s (task capacity = %s)",
                                        worker.name,
                                        exit_reason,
                                        worker.task_capacity,
                                    )
                                    break
                                else:
                                    logger.error(
                                        "%s: failed (task capacity = %s)",
                                        worker.name,
                                        worker.task_capacity,
                                        exc_info=True,
                                    )
                            else:
                                future.set_result(result)
                                logger.info(
                                    "%s: succeeded (task capacity = %s)",
                                    worker.name,
                                    worker.task_capacity,
                                )
                        else:
                            logger.warning(
                                "%s: future cancelled (task capacity = %s)",
                                worker.name,
                                worker.task_capacity,
                            )
                    finally:
                        self._task_queue.task_done()

                    if worker.task_capacity <= 0:
                        exit_reason = "task capacity reached"
                        break
        except BaseException:
            logger.critical("Exception in worker", exc_info=True)
            raise

        try:
            logger.debug("%s: %s", worker.name, exit_reason)
            with self._shutdown_lock:
                self._workers.discard(worker)
                if not self._shutdown_flag:
                    if self._lazy_scheduling:
                        while self._require_more_workers():
                            self._start_worker()
                    else:
                        self._start_worker()
            logger.debug("%s: exiting", worker.name)
        except BaseException:
            logger.critical("Exception in worker exit", exc_info=True)
            raise

    @contextmanager
    def execute_context(
        self,
    ) -> ExecuteContextReturnType:
        def execute(
            task: callable, args: tuple, kwargs: dict, future: futures.Future
        ) -> Any:
            return task(*args, **kwargs)

        def worker_exit_msg() -> Optional[str]:
            """Return exit message in case the executor worker must exit."""
            return

        yield (execute, worker_exit_msg)
