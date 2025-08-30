"""SLURM API to submit, cancel and monitor scripts that start a python process
to establish a connection over which python functions can be executed."""

import logging
from typing import Optional, Union

from .script import SlurmScriptRestClient
from ..job_io.local import RemoteWorkerProxy

from .. import defaults

logger = logging.getLogger(__name__)


class SlurmPyConnRestClient(SlurmScriptRestClient):
    """SLURM API to submit, cancel and monitor scripts that start a python process
    to establish a connection over which python functions can be executed.
    This class does not contain any job-related state."""

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
        """
        self.pre_script = pre_script
        self.post_script = post_script
        self.python_cmd = python_cmd
        super().__init__(
            url=url,
            user_name=user_name,
            token=token,
            api_version=api_version,
            renewal_url=renewal_url,
            parameters=parameters,
            log_directory=log_directory,
            std_split=std_split,
            request_options=request_options,
            use_os_environment=use_os_environment,
        )

    def submit_script(
        self,
        worker_proxy: RemoteWorkerProxy,
        pre_script: Optional[str] = None,
        post_script: Optional[str] = None,
        python_cmd: Optional[str] = None,
        parameters: Optional[dict] = None,
        metadata: Optional[Union[str, dict]] = None,
        request_options: Optional[dict] = None,
    ) -> int:
        """Submit a script that will establish a connection initialized in the current process."""
        if parameters is None:
            parameters = dict()

        environment = parameters.setdefault("environment", dict())
        environment.update(worker_proxy.remote_environment)

        if not metadata:
            metadata = dict()
        metadata.update(worker_proxy.metadata)

        script = self._make_executable(
            worker_proxy.remote_script(),
            pre_script=pre_script,
            post_script=post_script,
            python_cmd=python_cmd,
        )

        return super().submit_script(
            script=script,
            parameters=parameters,
            metadata=metadata,
            request_options=request_options,
        )

    def _make_executable(
        self,
        python_script: str,
        pre_script: Optional[str] = None,
        post_script: Optional[str] = None,
        python_cmd: Optional[str] = None,
    ) -> str:
        """Make a python script executable."""
        if not pre_script:
            pre_script = self.pre_script
        if not post_script:
            post_script = self.post_script
        if not python_cmd:
            python_cmd = self.python_cmd
        if not python_cmd:
            python_cmd = defaults.PYTHON_CMD
        if not pre_script and not post_script:
            return f"#!/usr/bin/env {python_cmd}\n{python_script}"
        if not pre_script:
            pre_script = ""
        if not post_script:
            post_script = ""
        return f"{pre_script}\ntype {python_cmd}\n{python_cmd} <<'EOF'\n{python_script}EOF\n\n{post_script}"
