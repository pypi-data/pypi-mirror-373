import os
import abc
import sys
import inspect
import logging
from typing import Any, Optional, Tuple, Union

if sys.version_info >= (3, 8):
    from importlib.metadata import metadata as distribution_metadata
else:
    from importlib_metadata import metadata as distribution_metadata

from ... import errors


logger = logging.getLogger(__name__)

TASK = Union[callable, str]


class WorkerProxy:
    """Worker proxy to execute tasks with an optional maximum and an initializer.

    .. code-block::

        with WorkerProxy(initializer=..., initargs=..., initkwargs=..., max_tasks=...) as proxy:
            proxy.initialize()  # optionally explicit
            # -> max_tasks(int)
            # -> initializer(callable), initargs(tuple), initkwargs(dict), None
            # <- result, exception

            result1 = proxy.execute(task1, args1, kwargs1)
            # -> task1(callable), args1(tuple), kwargs1(dict)
            # <- result, exception

            result2 = proxy.execute(task2, args2, kwargs2)
            # -> task2(callable), args2(tuple), kwargs2(dict)
            # <- result, exception

            ...

            proxy.close()  # optionally explicit
            # -> None
    """

    def __init__(
        self,
        initializer: Optional[callable] = None,
        initargs: Optional[tuple] = None,
        initkwargs: Optional[tuple] = None,
        max_tasks: Optional[int] = None,
    ) -> None:
        """
        :param initializer: execute before the first task
        :param initargs: parameters for `initializer`
        :param initkwargs: parameters for `initializer`
        :param max_tasks: maximum number of tasks this proxy can execute
        """
        self._close_flag = False
        self._always_source = False

        self._initializer = initializer
        self._initargs = initargs
        self._initkwargs = initkwargs
        self._initial_send = False

        if max_tasks is not None and initializer is not None:
            # Initializers are send like any other task, only during initialization
            # and a failure will close the proxy.
            max_tasks += 1
        self._max_tasks = max_tasks
        self._task_counter = 0

    def close(self):
        if not self._close_flag:
            self._send_when_not_closed(None)
            self._close_flag = True

    def __enter__(self) -> "WorkerProxy":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def initialize(self) -> None:
        """Initialize the communication with the client. Will be done automatically upon the first `submit` call
        when not called explicitly. Re-raises the remote exception when the initializer fails.
        """
        if self._initial_send:
            return
        initial_data = self._max_tasks, logging.getLogger().getEffectiveLevel()
        self._send_when_not_closed(initial_data)
        self._initial_send = True
        if self._initializer is not None:
            try:
                _ = self.execute(self._initializer, self._initargs, self._initkwargs)
            except BaseException:
                self.close()
                raise

    def execute_without_reraise(
        self,
        task: Optional[callable],
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
    ) -> Tuple[Any, errors.SerializedException]:
        """Send the task to the client and wait for the result."""
        self.initialize()

        task_org = task
        if task is not None:
            task = _callable_or_source_code(task, always_source=self._always_source)

        self._send_when_not_closed((task, args, kwargs))
        self._task_counter += 1

        if task_org is None:
            logger.debug("stop request submitted to the remote worker")
        else:
            logger.debug("%s submitted to the remote worker", task_org)

        try:
            return self._get_result()
        finally:
            if self._max_tasks is not None and self._task_counter >= self._max_tasks:
                self.close()

    def execute(
        self,
        task: Optional[callable],
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
    ) -> Any:
        """Send the task to the client and wait for the result.
        When the task failed remotely, re-raise the exection locally.
        """
        result, exc_info = self.execute_without_reraise(task, args=args, kwargs=kwargs)
        if exc_info is not None:
            errors.reraise_remote_exception_from_tb(exc_info)
        return result

    def _send_when_not_closed(self, data: Any) -> None:
        if self._close_flag:
            raise RuntimeError("cannot send data after stopped")
        self._send(data)

    @abc.abstractmethod
    def _send(self, data: Any) -> None:
        pass

    @abc.abstractmethod
    def _get_result(self) -> Tuple[Any, Optional[errors.SerializedException]]:
        """In case of an exception, it could be raised (local error) or
        returned serialized (remote error)."""
        pass


def _callable_or_source_code(
    func: callable, always_source: bool = False
) -> Union[callable, Tuple[str, str]]:
    try:
        try:
            filename = inspect.getfile(func)
        except Exception:
            # For example a python builtin function
            return func
        if not filename or not os.path.isfile(filename):
            return func

        if not always_source:
            try:
                module = inspect.getmodule(func)
                package_name = module.__name__.split(".")[0]
                # TODO: distribution name and package name are not always the same
                _ = distribution_metadata(package_name)
            except Exception:
                pass
            else:
                if not module.__name__.startswith("pyslurmutils.tests"):
                    return func

        with open(filename, "r") as file:
            source_code = []
            for line in file.readlines():
                source_code.append(_safe_import(line))

        return func.__name__, "".join(source_code)
    except Exception:
        return func


def _safe_import(line: str) -> str:
    if line.startswith("import "):
        # Get the module name after 'import'
        module_name = line.split("import ")[1].split(" as ")[0].strip()
        return f"try:\n    {line.rstrip()}\nexcept ImportError:\n    {module_name} = None\n"
    if line.startswith("from "):
        # Get the module or name after 'from'
        module_name = line.split("import")[0].replace("from", "").strip()
        object_names = line.split("import")[1].split(" as ")[0].strip()
        n = len(object_names.replace(" ", "").split(","))
        if n > 1:
            values = ", ".join(("None",) * n)
        else:
            values = "None"
        return f"try:\n    {line.rstrip()}\nexcept ImportError:\n    {object_names} = {values}\n"
    return line
