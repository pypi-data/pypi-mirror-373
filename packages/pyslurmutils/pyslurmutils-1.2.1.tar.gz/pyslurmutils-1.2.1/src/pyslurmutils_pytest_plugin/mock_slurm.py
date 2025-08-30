import os
import sys
import json
import time
import logging
import pathlib
import threading
import functools
import subprocess
from urllib.parse import urlparse
from typing import Optional, Dict, Tuple, Union, List
from unittest.mock import patch
from tempfile import NamedTemporaryFile
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor

import pytest
import requests

logger = logging.getLogger(__name__)

_MAX_JOBS = 50


@contextmanager
def mock_slurm_clients(tmp_path: pathlib.Path, slurm_parameters: Dict[str, str]):
    # Ensure `pyslurmutils` is not imported when `pyslurmutils_pytest_plugin` is imported.
    # When a package is imported before the `pytest_cov` coverage starts a `CoverageWarning`
    # is raised at the end of testing `pyslurmutils` itself.
    from pyslurmutils.client import defaults
    from pyslurmutils.client.rest.api import slurm_access

    last_job_id = 0
    jobs = dict()
    api_version_str = slurm_parameters["api_version"] or defaults.DEFAULT_API_VERSION
    api_version_tuple = slurm_access.parse_version(api_version_str)

    class MockResponse(requests.Response):
        def __init__(self, json_data, status_code: int):
            super().__init__()
            self.encoding = "utf-8"
            self._content = json.dumps(json_data).encode(self.encoding)
            self.status_code = status_code
            self.headers["Content-Type"] = "application/json"

    def _mock_request(
        method: str, url: str, json: Optional[dict] = None, **_
    ) -> MockResponse:
        nonlocal last_job_id

        parsed_url = urlparse(url)
        assert parsed_url.scheme == "http", url
        assert parsed_url.hostname == "mockhost", url
        assert parsed_url.port == 6820, url
        assert parsed_url.username is None, url
        path = parsed_url.path

        if (method, path) == ("GET", "/openapi"):
            return MockResponse(
                {
                    "paths": {
                        f"/slurm/{api_version_str}/job/submit": {},
                    }
                },
                200,
            )

        if method == "GET" and path.startswith(f"/slurm/{api_version_str}/job/"):
            job_id = int(path.split("/")[-1])
            job = jobs.get(job_id)
            if job is None:
                return MockResponse(
                    {
                        "last_backfill": {"set": False, "infinite": False, "number": 0},
                        "last_update": {"set": False, "infinite": False, "number": 0},
                        "warnings": [],
                        "errors": [],
                    },
                    404,
                )
            job_exec_info = job["job_exec_info"]
            logger.debug(
                "SLURM mock backend: get job %s %s", job_id, job_exec_info["job_state"]
            )
            return MockResponse(
                {
                    "jobs": [job_exec_info],
                    "last_backfill": {"set": False, "infinite": False, "number": 0},
                    "last_update": {"set": False, "infinite": False, "number": 0},
                    "warnings": [],
                    "errors": [],
                },
                200,
            )

        if method == "GET" and path == f"/slurm/{api_version_str}/jobs":
            logger.debug("SLURM mock backend: get jobs (# %d)", len(jobs))
            return MockResponse(
                {
                    "jobs": [job["job_exec_info"] for job in jobs.values()],
                    "last_backfill": {"set": False, "infinite": False, "number": 0},
                    "last_update": {"set": False, "infinite": False, "number": 0},
                    "warnings": [],
                    "errors": [],
                },
                200,
            )

        if method == "GET":
            raise NotImplementedError(path)

        if method == "DELETE" and path.startswith(f"/slurm/{api_version_str}/job/"):
            job_id = int(path.split("/")[-1])
            job = jobs.get(job_id)
            if job is None:
                return MockResponse(
                    {
                        "warnings": [],
                        "errors": [],
                    },
                    404,
                )
            job_exec_info = job["job_exec_info"]
            with job["job_state_lock"]:
                job_exec_info["job_state"] = _job_state("CANCELLED", api_version_tuple)
                logger.debug("SLURM mock backend: cancel job %s", last_job_id)
                return MockResponse(
                    {
                        "warnings": [],
                        "errors": [],
                    },
                    200,
                )

        if method == "DELETE":
            raise NotImplementedError(path)

        if path == f"/slurm/{api_version_str}/job/submit":
            last_job_id += 1
            job_exec_info = {
                "job_id": last_job_id,
                "job_state": _job_state("PENDING", api_version_tuple),
                **json["job"],
                "user_name": slurm_parameters["user_name"],
                "warnings": [],
                "errors": [],
            }
            job = {"job_exec_info": job_exec_info, "job_state_lock": threading.Lock()}
            jobs[last_job_id] = job
            logger.debug("SLURM mock backend: recieved job %s", last_job_id)

            if api_version_tuple < (0, 0, 39):
                script = json["script"]
            else:
                script = json["job"]["script"]

            lines = script.split("\n")
            shebang = lines[0]
            if "bash" in shebang:
                if sys.platform == "win32":
                    pytest.skip("bash script does not run on windows")
            elif "python" in shebang:
                pass
            else:
                assert False, f"Unknown script starting with '{shebang}'"

            future = slurm_queue.submit(
                _job_main, script, json, job, str(tmp_path), api_version_tuple
            )
            futures.append(future)
            return MockResponse(job_exec_info, 200)

        if method == "POST":
            raise NotImplementedError(path)

    futures = []
    with ThreadPoolExecutor(max_workers=_MAX_JOBS) as slurm_queue:
        with patch("requests.request", side_effect=_mock_request):
            yield
            for future in futures:
                _ = future.result()


def _absorb_exception(function):
    @functools.wraps(function)
    def inner(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Job execution failed: {e}")

    return inner


@_absorb_exception
def _job_main(
    script: str,
    json: dict,
    job: dict,
    tmp_path: pathlib.Path,
    api_version: Tuple[int, int, int],
) -> None:
    job_state_lock = job["job_state_lock"]
    job_exec_info = job["job_exec_info"]
    cmd = []
    lines = script.split("\n")
    shebang = lines[0]
    if "bash" in shebang:
        suffix = ".sh"
    elif "python" in shebang:
        if sys.platform == "win32":
            lines.pop(0)
            cmd = [sys.executable]
        suffix = ".py"
    else:
        assert False, f"Unknown script starting with '{shebang}'"

    with NamedTemporaryFile("w", delete=False, dir=tmp_path, suffix=suffix) as script:
        script.write("\n".join(lines))
        filename = script.name
    os.chmod(filename, 0o755)
    cmd.append(filename)

    env = dict(os.environ)
    for keyvalue in json["job"].get("environment", list()):
        key, _, value = keyvalue.partition("=")
        env[key] = value
    env["SLURM_JOB_ID"] = str(job_exec_info["job_id"])

    standard_output = json["job"].get("standard_output")
    standard_error = json["job"].get("standard_error")

    if standard_output is None:
        stdout = None
    elif standard_output == "/dev/null":
        stdout = None
        standard_output = None
    else:
        stdout = subprocess.PIPE

    if standard_error is None:
        stderr = None
    elif standard_error == "/dev/null":
        stderr = None
        standard_error = None
    else:
        stderr = stdout or subprocess.PIPE

    with subprocess.Popen(
        cmd, stdout=stdout, stderr=stderr, env=env, cwd=os.getcwd()
    ) as proc:
        job_id = job_exec_info["job_id"]

        cancelled_state = _job_state("CANCELLED", api_version)
        running_state = _job_state("RUNNING", api_version)

        def monitor_cancellation():
            while proc.poll() is None:
                with job_state_lock:
                    if job_exec_info["job_state"] == cancelled_state:
                        logger.debug("SLURM mock backend: cancel job %s ...", job_id)
                        proc.terminate()
                        break
                    elif job_exec_info["job_state"] != running_state:
                        job_exec_info["job_state"] = running_state
                        logger.debug("SLURM mock backend: job %s started", job_id)
                time.sleep(1)

        # Start cancellation monitor thread
        cancel_thread = threading.Thread(target=monitor_cancellation, daemon=True)
        cancel_thread.start()
        try:
            try:
                outs, errs = proc.communicate(timeout=60)
            except subprocess.TimeoutExpired:
                proc.kill()
                outs, errs = proc.communicate()
                logger.warning("Job %s timed out and was killed", job_id)

            # Write output and error if not cancelled
            if job_exec_info["job_state"] == _job_state("CANCELLED", api_version):
                logger.debug("SLURM mock backend: job %s cancelled", job_id)
            else:
                if standard_output is not None:
                    outfile = standard_output.replace("%j", str(job_id))
                    with open(outfile, "wb") as f:
                        f.write(outs)

                if standard_error is not None:
                    errfile = standard_error.replace("%j", str(job_id))
                    with open(errfile, "wb") as f:
                        f.write(errs)

                if proc.returncode:
                    job_exec_info["job_state"] = _job_state("FAILED", api_version)
                    logger.debug("SLURM mock backend: job %s failed", job_id)
                else:
                    job_exec_info["job_state"] = _job_state("COMPLETED", api_version)
                    logger.debug("SLURM mock backend: job %s completed", job_id)
        finally:
            cancel_thread.join()


def _job_state(state: str, api_version: Tuple[int, int, int]) -> Union[str, List[str]]:
    if api_version < (0, 0, 40):
        return state
    return [state]
