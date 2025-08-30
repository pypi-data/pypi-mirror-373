"""Low-level SLURM API to submit, cancel and monitor jobs"""

import os
import time
import json
import logging
import datetime
from pprint import pformat
from urllib.parse import urlparse, urlunparse
from contextlib import contextmanager
from typing import List, Optional, Tuple, Union, Generator, Dict, Any

from .. import utils
from .. import defaults
from .. import os_utils
from .. import url_utils
from .api import slurm_logs
from .api import slurm_access
from .api import slurm_params
from .api import slurm_response
from .api import slurm_auth
from ..log_utils import log_file_monitor_context
from ..errors import SlurmInvalidUrlError
from ..errors import SlurmMissingParameterError

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SlurmBaseRestClient:
    """Low-level SLURM API to submit, cancel and monitor jobs.
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
        :param use_os_environment: Use ``SLURM_*`` environment variables
        :raises SlurmMissingParameterError:
        :raises SlurmTokenInvalidError:
        :raises SlurmInvalidUrlError:
        """
        if not url and use_os_environment:
            url = os.environ.get("SLURM_URL")
        if not url:
            raise SlurmMissingParameterError(
                "'url' must be provided or set environment variable SLURM_URL"
            )
        self._base_url = _parse_slurm_rest_url(url)

        self._auth = slurm_auth.SlurmAuthManager(
            user_name=user_name,
            token=token,
            renewal_url=renewal_url,
            use_os_environment=use_os_environment,
        )

        if not api_version and use_os_environment:
            api_version = os.environ.get("SLURM_API_VERSION")
        if not api_version:
            api_version = defaults.DEFAULT_API_VERSION
        version_tuple = slurm_access.parse_version(api_version)
        self._api_version_str: str = slurm_access.create_version(version_tuple)
        self._api_version_tuple: Tuple[int, int, int] = version_tuple

        self._parameters = parameters
        if log_directory:
            log_directory = str(log_directory).format(user_name=user_name)
        self._log_directory = log_directory
        self._std_split = std_split
        self._request_options = request_options

    def submit_job(
        self,
        script: str,
        parameters: Optional[dict] = None,
        metadata: Optional[Union[str, dict]] = None,
        request_options: Optional[dict] = None,
    ) -> int:
        """Returns the SLURM job ID"""
        # Job parameters
        parameters = utils.merge_mappings(self._parameters, parameters)
        self._submit_ensure_name(parameters)
        self._submit_ensure_std(parameters)
        self._submit_ensure_environment(parameters)
        self._submit_ensure_wd(parameters)
        if metadata:
            if not isinstance(metadata, str):
                metadata = json.dumps(metadata)
            parameters["comment"] = metadata
        slurm_params.coerce_parameters(self._api_version_tuple, parameters)

        # Request body
        body = {"job": parameters}
        if request_options:
            request_options["json"] = body
        else:
            request_options = {"json": body}

        # Job script
        if self._api_version_tuple < (0, 0, 39):
            body["script"] = script
        else:
            body["job"]["script"] = script

        # Submit job
        response = self.post(
            f"/slurm/{self._api_version_str}/job/submit",
            request_options=request_options,
        )

        # Log submission
        job_name = parameters["name"]
        job_id = response.job_id
        user_msg = response.job_submit_user_msg
        if user_msg:
            logger.info(
                "SLURM job '%s' submitted (Job ID: %s): %s", job_name, job_id, user_msg
            )
        else:
            logger.info("SLURM job '%s' submitted (Job ID: %s)", job_name, job_id)

        return job_id

    def _submit_ensure_name(self, parameters: dict) -> None:
        if not parameters.get("name"):
            parameters["name"] = defaults.JOB_NAME

    def _submit_ensure_std(self, parameters: dict) -> None:
        parameters["standard_input"] = "/dev/null"
        if self._log_directory:
            os_utils.makedirs(self._log_directory)
            job_name = parameters["name"]
            filetemplate = f"{self._log_directory}/{job_name}.%j"
            if self._std_split:
                parameters["standard_output"] = f"{filetemplate}.out"
                parameters["standard_error"] = f"{filetemplate}.err"
            else:
                parameters["standard_output"] = f"{filetemplate}.outerr"
        else:
            parameters["standard_output"] = "/dev/null"
            parameters["standard_error"] = "/dev/null"

    def _submit_ensure_environment(self, parameters: dict) -> None:
        if parameters.get("environment"):
            return
        parameters["environment"] = {"_DUMMY_VAR": "dummy_value"}

    def _submit_ensure_wd(self, parameters: dict) -> None:
        if not parameters.get("current_working_directory"):
            parameters["current_working_directory"] = (
                "/tmp"  # TODO: this does not work: "~"
            )

    def cancel_job(self, job_id: int, request_options: Optional[dict] = None) -> None:
        request_options = utils.merge_mappings(
            request_options, {"path_params": {"job_id": job_id}}
        )

        _ = self.delete(
            f"/slurm/{self._api_version_str}/job/{{job_id}}",
            request_options=request_options,
        )

    def clean_job_artifacts(
        self,
        job_id: int,
        job_properties: Optional[BaseModel] = None,
        request_options: Optional[dict] = None,
    ) -> None:
        if job_properties is None:
            job_properties = self.get_job_properties(
                job_id, raise_on_error=False, request_options=request_options
            )
        if job_properties is None:
            return
        slurm_logs.remove_slurm_log(job_properties, stderr=False)
        slurm_logs.remove_slurm_log(job_properties, stderr=True)

    @contextmanager
    def clean_job_artifacts_context(
        self,
        job_id: int,
        job_properties: Optional[BaseModel] = None,
        request_options: Optional[dict] = None,
    ) -> Generator[None, None, None]:
        try:
            yield
        finally:
            self.clean_job_artifacts(
                job_id,
                job_properties=job_properties,
                request_options=request_options,
            )

    def get_job_properties(
        self, job_id: int, raise_on_error=True, request_options: Optional[dict] = None
    ) -> Optional[BaseModel]:
        request_options = utils.merge_mappings(
            request_options, {"path_params": {"job_id": job_id}}
        )

        response = self.get(
            f"/slurm/{self._api_version_str}/job/{{job_id}}",
            request_options=request_options,
            raise_on_error=raise_on_error,
        )

        if response is None:
            return
        if not response.jobs:
            return
        return response.jobs[0]

    def get_all_job_properties(
        self,
        raise_on_error=True,
        request_options: Optional[dict] = None,
        filter: Optional[dict] = None,
        update_time: Optional[datetime.datetime] = None,
        all_users: bool = False,
    ) -> List[BaseModel]:
        # Server-side filter
        if update_time:
            request_options = utils.merge_mappings(
                request_options,
                {"query_params": {"update_time": update_time.timestamp()}},
            )

        response = self.get(
            f"/slurm/{self._api_version_str}/jobs",
            request_options=request_options,
            raise_on_error=raise_on_error,
        )
        if response is None or not response.jobs:
            return list()

        # Client-side filter
        if not filter:
            filter = dict()
        if not all_users:
            filter.setdefault("user_name", self._auth.user_name)

        return [
            job_properties
            for job_properties in response.jobs
            if self._is_part_of(job_properties, filter)
        ]

    def _is_part_of(self, obj: Any, subobj: Any) -> bool:
        """Check that `subobj` is a part of `obj`."""
        if isinstance(subobj, dict):
            # subobj must be a sub-tree of obj
            if not isinstance(obj, (dict, BaseModel)):
                return False
            for subobj_key, subobj_value in subobj.items():
                if isinstance(obj, BaseModel):
                    if not hasattr(obj, subobj_key):
                        return False
                    obj_value = getattr(obj, subobj_key)
                else:
                    if subobj_key not in obj:
                        return False
                    obj_value = obj[subobj_key]
                if not self._is_part_of(obj_value, subobj_value):
                    return False
            return True
        elif isinstance(subobj, list):
            # subobj must be equal to obj[:len(subobj)]
            if not isinstance(obj, list):
                return False
            if len(subobj) > len(obj):
                return False
            for obj_item, subobj_item in zip(obj, subobj):
                if not self._is_part_of(obj_item, subobj_item):
                    return False
            return True
        else:
            return obj == subobj

    def get_status(self, job_id: int, request_options: Optional[dict] = None) -> str:
        job_properties = self.get_job_properties(
            job_id, request_options=request_options
        )
        return slurm_response.slurm_job_state(job_properties)

    def get_full_status(
        self, job_id: int, request_options: Optional[dict] = None
    ) -> dict:
        job_properties = self.get_job_properties(
            job_id, request_options=request_options
        )
        return slurm_response.slurm_job_full_state(job_properties)

    def is_finished(self, job_id: int) -> bool:
        """Returns `True` when the job is completely finished."""
        return self.get_status(job_id) in slurm_response.FINISHED_STATES

    def is_finishing(self, job_id: int, request_options: Optional[dict] = None) -> bool:
        """Returns `True` when the job is finished by Slurm is still finalizing."""
        return self.get_status(job_id) in slurm_response.FINISHING_STATES

    def wait_finished(self, job_id: int, **kw) -> str:
        """Wait until a job is finished and return the state."""
        return self.wait_states(job_id, slurm_response.FINISHED_STATES, **kw)

    def wait_finishing(self, job_id: int, **kw) -> str:
        """Wait until a job is finished or in the process of finishing and return the state."""
        return self.wait_states(job_id, slurm_response.FINISHING_STATES, **kw)

    def wait_states(
        self,
        job_id: int,
        states: Tuple[str],
        progress: bool = False,
        timeout: Optional[float] = None,
        period: float = 0.5,
    ) -> str:
        """Wait until a job state is reached and return the state."""
        job_state = None
        t0 = time.time()
        while job_state not in states:
            job_state = self.get_status(job_id)
            time.sleep(period)
            if progress:
                print(".", end="", flush=True)
            if timeout is not None and (time.time() - t0) > timeout:
                raise TimeoutError
        status = self.get_full_status(job_id)
        logger.info("Job '%s' finished: %s", job_id, pformat(status))
        return job_state

    def print_stdout_stderr(
        self, job_id: int, request_options: Optional[dict] = None
    ) -> None:
        job_properties = self.get_job_properties(
            job_id, request_options=request_options, raise_on_error=False
        )
        if job_properties is None:
            return

        stdout, stderr = slurm_logs.get_stdout_stderr(job_properties)
        print()
        print("".join(stdout.lines()))
        if stderr is not None:
            print("".join(stderr.lines()))

    def log_stdout_stderr(
        self,
        job_id: int,
        logger: Optional[logging.Logger] = None,
        level: int = logging.INFO,
        request_options: Optional[dict] = None,
        **log_options,
    ) -> None:
        job_properties = self.get_job_properties(
            job_id, request_options=request_options, raise_on_error=False
        )
        if job_properties is None:
            return

        stdout, stderr = slurm_logs.get_stdout_stderr(job_properties)
        stdout = "".join(stdout.lines())

        if logger is None:
            logger = logger
        if stderr is None:
            logger.log(level, "\n%s", stdout, **log_options)
        else:
            stderr = "".join(stderr.lines())
            logger.log(level, "\n%s\n%s", stdout, stderr, **log_options)

    @contextmanager
    def redirect_stdout_stderr(
        self, job_id: int, request_options: Optional[dict] = None
    ) -> Generator[None, None, None]:
        """Redirect logs files to the local root logger within this context."""
        job_properties = self.get_job_properties(
            job_id, raise_on_error=False, request_options=request_options
        )
        if job_properties is None:
            yield
            return

        ofilename = slurm_logs.slurm_log_filename(
            job_properties, job_properties.standard_output
        )
        efilename = slurm_logs.slurm_log_filename(
            job_properties, job_properties.standard_error
        )
        with log_file_monitor_context([ofilename, efilename]):
            yield

    def get(self, path: str, **kwargs) -> Optional[BaseModel]:
        return self.request("GET", path, **kwargs)

    def delete(self, path: str, **kwargs) -> Optional[BaseModel]:
        return self.request("DELETE", path, **kwargs)

    def post(self, path: str, **kwargs) -> Optional[BaseModel]:
        return self.request("POST", path, **kwargs)

    def request(
        self,
        method: str,
        path: str,
        request_options: Optional[dict] = None,
        raise_on_error: bool = True,
    ) -> Optional[BaseModel]:
        request_options = self._merged_request_options(request_options)
        try:
            return slurm_access.validated_slurm_request(
                method, self._base_url, path, **request_options
            )
        except Exception as e:
            headers = self._auth.retry_headers()
            if not headers:
                if raise_on_error:
                    raise
                logger.debug(str(e))
                return None
            request_options["headers"] = headers

        try:
            return slurm_access.validated_slurm_request(
                method, self._base_url, path, **request_options
            )
        except Exception as e:
            if raise_on_error:
                raise
            logger.debug(str(e))
        return None

    def server_has_api(
        self, request_options: Optional[dict] = None
    ) -> Union[bool, str, List[str]]:
        request_options = self._merged_request_options(request_options)

        openapi_spec = None
        try:
            openapi_spec = slurm_access.slurm_request(
                "GET", self._base_url, "/openapi", **request_options
            )
        except Exception:
            headers = self._auth.retry_headers()
            if not headers:
                raise
            request_options["headers"] = headers
        if openapi_spec is None:
            openapi_spec = slurm_access.slurm_request(
                "GET", self._base_url, "/openapi", **request_options
            )

        versions = slurm_response.extract_slurm_api_versions(openapi_spec)
        has_api = self._api_version_tuple in versions
        versions = [slurm_access.create_version(v) for v in versions]
        return has_api, self._api_version_str, versions

    def _merged_request_options(
        self,
        request_options: Optional[dict] = None,
    ) -> Dict[str, Any]:
        # self._auth > request_options > self._request_options
        headers = {"headers": self._auth.headers()}
        request_options = utils.merge_mappings(request_options, headers)
        request_options = utils.merge_mappings(self._request_options, request_options)
        return request_options


def _parse_slurm_rest_url(slurm_url: str, default_port: int = 6820) -> str:
    """
    :raises SlurmInvalidUrlError:
    """
    parsed = urlparse(slurm_url)
    if not parsed.scheme:
        raise SlurmInvalidUrlError(
            f"Empty SLURM REST URL scheme: {parsed.scheme}. Expected 'http' or 'https'."
        )

    if not parsed.hostname:
        raise SlurmInvalidUrlError("Missing hostname.")

    if parsed.port is None:
        parsed = url_utils.set_url_port(parsed, default_port)

    return urlunparse(parsed)
