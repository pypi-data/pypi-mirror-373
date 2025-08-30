from typing import Any, Tuple, Optional

from ._proxy_base import WorkerProxy


class LocalWorkerProxy(WorkerProxy):
    """Worker proxy which executes tasks in the current process."""

    def __init__(
        self,
        initializer: Optional[callable] = None,
        initargs: Optional[tuple] = None,
        initkwargs: Optional[tuple] = None,
        max_tasks: Optional[int] = None,
    ) -> None:
        self._data = None
        super().__init__(
            initializer=initializer,
            initargs=initargs,
            initkwargs=initkwargs,
            max_tasks=max_tasks,
        )

    def _send(self, data: Any) -> None:
        self._data = data

    def _get_result(self) -> Tuple[Any, None]:
        try:
            if isinstance(self._data, tuple):
                task, args, kwargs = self._data
                if args is None:
                    args = tuple()
                if kwargs is None:
                    kwargs = dict()
                if isinstance(task, tuple):
                    func_name, source_code = task
                    lcls = locals()
                    dunder_name = lcls.get("__name__", None)
                    lcls["__name__"] = "__notmain__"
                    try:
                        exec(source_code, globals(), lcls)
                    finally:
                        if dunder_name:
                            lcls["__name__"] = dunder_name
                    func = lcls[func_name]
                    result = func(*args, **kwargs)
                else:
                    result = task(*args, **kwargs)
                return result, None
        finally:
            self._data = None
        return None, None
