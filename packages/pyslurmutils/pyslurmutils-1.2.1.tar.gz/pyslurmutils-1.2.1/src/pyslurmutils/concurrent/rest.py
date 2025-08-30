import logging
import weakref
import warnings
from pprint import pformat
from concurrent import futures
from contextlib import ExitStack
from contextlib import contextmanager
from typing import Optional, Any, Tuple, Type

from ..client import errors
from ..client import defaults
from ..client import SlurmPyConnRestClient
from ..client.rest.api import slurm_response
from ..client.job_io.local import RemoteExecutor
from ..client.job_io.local import ExecutorShutdown
from ..client.job_io.local import ExecuteContextReturnType
from ..client.job_io.local import RemoteWorkerProxy
from ..client.job_io.local import FileConnection
from ..client.job_io.local import TcpConnection


logger = logging.getLogger(__name__)


class SlurmRestFuture(futures.Future):
    def __init__(self) -> None:
        self._job_id = None
        self._slurm_client = None
        self._delayed_cancel_job = False
        super().__init__()

    def job_submitted(self, job_id: int, slurm_client: SlurmPyConnRestClient) -> None:
        """The SLURM job was submitted. Beware that the Slurm job may be running other tasks as well."""
        self._job_id = job_id
        self._slurm_client = weakref.proxy(slurm_client)
        if self._delayed_cancel_job:
            slurm_client.cancel_job(job_id)

    @property
    def job_id(self) -> Optional[int]:
        return self._job_id

    @property
    def slurm_client(self) -> Optional[SlurmPyConnRestClient]:
        return self._slurm_client

    def cancel_job(self) -> None:
        warnings.warn(
            "`cancel_job()` is deprecated and will be removed in a future release. Use `abort()` instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def abort(self) -> bool:
        """Cancel the Slurm job, even when it is already running. Beware that the Slurm job may be running other tasks as well."""
        slurm_client = self.slurm_client

        # The SLURM job was asked to be cancelled but didn't start yet: use `_delayed_cancel_job` to cancel it after it started.
        if slurm_client is None:
            self._delayed_cancel_job = True
        else:
            slurm_client.cancel_job(self.job_id)
        return self.aborted()

    def aborted(self) -> bool:
        slurm_client = self.slurm_client
        if slurm_client is None:
            return False
        status = slurm_client.get_status(self.job_id)
        return status == "CANCELLED"


class SlurmRestExecutor(RemoteExecutor):
    _FUTURE_CLASS = SlurmRestFuture

    def __init__(
        self,
        url: str = "",
        user_name: str = "",
        token: str = "",
        api_version: str = "",
        renewal_url: str = "",
        parameters: Optional[dict] = None,
        log_directory: Optional[str] = None,
        std_split: Optional[bool] = False,
        request_options: Optional[dict] = None,
        pre_script: Optional[str] = None,
        post_script: Optional[str] = None,
        python_cmd: Optional[str] = None,
        initializer: Optional[callable] = None,
        initargs: Optional[tuple] = None,
        initkwargs: Optional[tuple] = None,
        data_directory: Optional[str] = None,
        max_workers: Optional[int] = None,
        max_tasks_per_worker: Optional[int] = 1,
        lazy_scheduling: bool = True,
        conservative_scheduling: bool = False,
        cleanup_job_artifacts: bool = False,
        use_os_environment: bool = True,
    ):
        """
        :param url: SLURM REST API URL (fallback to SLURM_URL env)
        :param user_name: SLURM username (fallback to SLURM_USER or system user)
        :param token: SLURM JWT token (fallback to SLURM_TOKEN env)
        :param api_version: SLURM API version (e.g. 'v0.0.41')
        :param renewal_url: Url for SLURM JWT token renewal (fallback to SLURM_RENEWAL_URL env)
        :param parameters: SLURM job parameters
        :param log_directory: SLURM log directory
        :param std_split: Split standard output and standard error
        :param request_options: GET, POST and DELETE options
        :param pre_script: Shell script to execute at the start of a job
        :param post_script: Shell script to execute at the end of a job
        :param python_cmd: Python command
        :param initializer: execute when starting a job
        :param initargs: parameters for `initializer`
        :param initkwargs: parameters for `initializer`
        :param data_directory: communicate with the Slum job through files when specified
        :param max_workers: maximum number of Slum jobs that can run at any given time. `None` means unlimited.
        :param max_tasks_per_worker: maximum number of tasks each Slum job can receive before exiting. `None` means unlimited.
        :param lazy_scheduling: schedule SLURM jobs only when needed. Can only be disabled when `max_workers` is specified.
        :param conservative_scheduling: schedule the least amount of workers at the expense of tasks staying longer in the queue.
        :param cleanup_job_artifacts: cleanup job artifacts like logs.
        :param use_os_environment: Use ``SLURM_*`` environment variables
        """

        self._proxy_kwargs = {
            "max_tasks": max_tasks_per_worker,
            "initializer": initializer,
            "initargs": initargs,
            "initkwargs": initkwargs,
        }

        if data_directory:
            self._file_connection_kwargs = {
                "directory": data_directory,
                "basename": defaults.JOB_NAME,
            }
        else:
            self._file_connection_kwargs = None

        self._cleanup_job_artifacts = cleanup_job_artifacts

        self._slurm_client = SlurmPyConnRestClient(
            url=url,
            user_name=user_name,
            token=token,
            api_version=api_version,
            renewal_url=renewal_url,
            log_directory=log_directory,
            parameters=parameters,
            std_split=std_split,
            request_options=request_options,
            pre_script=pre_script,
            post_script=post_script,
            python_cmd=python_cmd,
            use_os_environment=use_os_environment,
        )

        super().__init__(
            max_workers=max_workers,
            max_tasks_per_worker=max_tasks_per_worker,
            lazy_scheduling=lazy_scheduling,
            conservative_scheduling=conservative_scheduling,
        )

    @contextmanager
    def execute_context(self) -> ExecuteContextReturnType:
        with ExitStack() as stack:

            job_id = None
            first_submit_kw = None

            def initialize(submit_kw):
                """
                Initialize SLURM worker: submit the SLURM job and initialize
                the communication with the worker.
                """
                nonlocal job_id, first_submit_kw
                first_submit_kw = submit_kw
                if submit_kw is None:
                    submit_kw = dict()
                job_id = self._slurm_client.submit_script(worker_proxy, **submit_kw)
                log_ctx = self._slurm_client.redirect_stdout_stderr(job_id)
                _ = stack.enter_context(log_ctx)

                if self._cleanup_job_artifacts:
                    cleanup_ctx = self._slurm_client.clean_job_artifacts_context(job_id)
                    _ = stack.enter_context(cleanup_ctx)

                worker_proxy.initialize()

            def execute(
                task: callable, args: tuple, kwargs: dict, future: SlurmRestFuture
            ) -> Any:
                """
                Send a task to the SLURM worker. Start the worker when not already running.
                """
                submit_kw = kwargs.pop(defaults.SLURM_ARGUMENTS_NAME, None)
                if job_id is None:
                    initialize(submit_kw)
                elif submit_kw != first_submit_kw:
                    logger.warning(
                        "SLURM submit arguments\n %s\n are ignored in favor of the arguments of the first task\n %s",
                        pformat(submit_kw),
                        pformat(first_submit_kw),
                    )

                future.job_submitted(job_id, self._slurm_client)

                try:
                    result, exc_info = worker_proxy.execute_without_reraise(
                        task, args=args, kwargs=kwargs
                    )
                except (ExecutorShutdown, errors.RemoteExit):
                    raise
                except Exception as ex:
                    exc_type, error_msg = status_error()
                    if exc_type:
                        raise exc_type(error_msg) from ex
                    raise

                if exc_info is not None:
                    errors.reraise_remote_exception_from_tb(exc_info)
                return result

            def status_error() -> Tuple[Optional[Type[Exception]], Optional[str]]:
                """Returns status exception class and message in case of a status error:
                remote Slurm job exited or local executor is shutting down.
                """
                if job_id is None:
                    return None, None
                try:
                    status = self._slurm_client.get_status(job_id)
                except Exception as e:
                    if self._shutdown_flag:
                        return ExecutorShutdown, "Slurm REST executor is shutting down"
                    logger.warning("failed getting the job state: %s", e, exc_info=True)
                    status = None
                if status in slurm_response.FINISHING_STATES:
                    return errors.RemoteExit, f"SLURM job {job_id} {status}"
                return None, None

            def raise_on_status_error() -> None:
                """Raise exception when there is a status error."""
                exc_type, error_message = status_error()
                if exc_type:
                    raise exc_type(error_message) from None

            def worker_exit_msg() -> Optional[str]:
                """Return exit message in case the executor worker must exit, i.e.
                when there is a status error."""
                _, exit_msg = status_error()
                return exit_msg

            if self._file_connection_kwargs:
                conn_ctx = FileConnection(
                    **self._file_connection_kwargs,
                    raise_on_status_error=raise_on_status_error,
                )
            else:
                conn_ctx = TcpConnection(raise_on_status_error=raise_on_status_error)
            connection = stack.enter_context(conn_ctx)
            proxy_ctx = RemoteWorkerProxy(connection, **self._proxy_kwargs)
            worker_proxy = stack.enter_context(proxy_ctx)

            if not self._lazy_scheduling:
                try:
                    initialize(None)
                except Exception as e:
                    logger.warning(
                        "SLURM worker initialization failed: %s", e, exc_info=True
                    )

            yield (execute, worker_exit_msg)
