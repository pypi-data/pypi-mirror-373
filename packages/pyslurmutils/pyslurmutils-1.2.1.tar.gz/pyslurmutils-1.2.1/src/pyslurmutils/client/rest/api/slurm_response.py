import re
import datetime
from typing import Optional, Any, Tuple, List, Dict

from pydantic import BaseModel

_LOCAL_OFFSET = datetime.datetime.now().astimezone().utcoffset()

FINISHED_STATES = (
    "BOOT_FAIL",
    "CANCELLED",
    "COMPLETED",
    "DEADLINE",
    "FAILED",
    "NODE_FAIL",
    "OUT_OF_MEMORY",
    "PREEMPTED",
    "TIMEOUT",
)
FINISHING_STATES = "COMPLETING", *FINISHED_STATES

# https://slurm.schedmd.com/job_state_codes.html
#
# BOOT_FAIL     terminated due to node boot failure
# CANCELLED     cancelled by user or administrator
# COMPLETED     completed execution successfully; finished with an exit code of zero on all nodes
# DEADLINE      terminated due to reaching the latest acceptable start time specified for the job
# FAILED        completed execution unsuccessfully; non-zero exit code or other failure condition
# NODE_FAIL     terminated due to node failure
# OUT_OF_MEMORY experienced out of memory error
# PENDING       queued and waiting for initiation; will typically have a reason code specifying why it has not yet started
# PREEMPTED     terminated due to preemption; may transition to another state based on the configured PreemptMode and job characteristics
# RUNNING       allocated resources and executing
# SUSPENDED     allocated resources but execution suspended, such as from preemption or a direct request from an authorized user
# TIMEOUT       terminated due to reaching the time limit, such as those configured in slurm.conf or specified for the individual job


def slurm_integer(number: Any) -> Optional[int]:
    if isinstance(number, BaseModel):
        if number.set and not number.infinite and number.number is not None:
            return int(number.number)
    else:
        if number is not None:
            return int(number)


def slurm_float(number: Any) -> float:
    if isinstance(number, BaseModel):
        if number.infinite:
            return float("inf")
        if number.set and number.number is not None:
            return float(number.number)
        return float("nan")
    else:
        if number is not None:
            return float(number)


def slurm_unix_timestamp(number: Any) -> Optional[datetime.datetime]:
    epoch = slurm_integer(number)
    if epoch is not None:
        utc = datetime.datetime.utcfromtimestamp(epoch)
        local = utc + _LOCAL_OFFSET
        return local.astimezone()
    now = datetime.datetime.now().astimezone()
    return now.replace(microsecond=0)


def slurm_unix_timestamp_or_now(number: Any) -> datetime.datetime:
    dt = slurm_unix_timestamp(number)
    if dt is not None:
        return dt
    now = datetime.datetime.now().astimezone()
    return now.replace(microsecond=0)


def slurm_duration_minutes(number: Any) -> Optional[datetime.timedelta]:
    minutes = slurm_integer(number)
    if minutes is not None:
        return datetime.timedelta(minutes=minutes)


def slurm_error_messages(model: BaseModel) -> Tuple[List[str], str]:
    messages = []
    suffix = ""

    if isinstance(model.errors, list):
        errors = model.errors
    elif model.errors is not None:
        errors = [model.errors]
    else:
        errors = []

    for error in errors:
        if error.error_number in (5005, -1):
            # Errors observer when the SLURM token expired:
            #
            # [5005:Zero Bytes were transmitted or received]
            #  POST job/submit
            #  DELETE job/{job_id}
            #
            # [-1: Unspecified error]
            # GET job/{job_id}
            # GET jobs
            suffix = " (SLURM token expired?)"
        msg = (
            f"[{error.error_number}: {error.error}] {error.source}: {error.description}"
        )
        messages.append(msg)

    return messages, suffix


def slurm_warning_messages(method: str, path: str, model: BaseModel) -> List[str]:
    messages = list()
    for warning in model.warnings:
        msg = f"{method} {path} {warning.source}: {warning.description}"
        messages.append(msg)
    return messages


def slurm_job_state(job_properties: Optional[BaseModel]) -> str:
    return slurm_job_states(job_properties)[0]


def slurm_job_full_state(job_properties: Optional[BaseModel]) -> str:
    status = slurm_job_state(job_properties)
    if status == "NOJOB":
        return {
            "status": status,
            "description": "None",
            "reason": "None",
            "exit_code": "NaN",
        }
    return {
        "status": status,
        "description": job_properties.state_description,
        "reason": job_properties.state_reason,
        "exit_code": job_properties.exit_code,
    }


def slurm_job_states(job_properties: Optional[BaseModel]) -> List[str]:
    if job_properties is None:
        return ["NOJOB"]
    if isinstance(job_properties.job_state, list):
        return job_properties.job_state
    if isinstance(job_properties.job_state, str):
        return [job_properties.job_state]
    return ["UNKNOWN"]


def extract_slurm_api_versions(
    openapi_spec: Dict[str, Any],
) -> List[Tuple[int, int, int]]:
    """
    Get the list of supported SLURM REST API versions (newest first).
    """
    pattern = re.compile(r"\/slurm\/v([0-9\.]+)\/?.*")
    versions = set()
    for path in openapi_spec["paths"]:
        match = pattern.match(path)
        if match:
            version = match.group(1).split(".")
            version = tuple(map(int, version))
            versions.add(version)
    return sorted(versions)[::-1]
