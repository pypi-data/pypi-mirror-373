import pytest

from ..client import SlurmScriptRestClient


@pytest.fixture
def slurm_script_client(slurm_client_kwargs) -> SlurmScriptRestClient:
    slurm_client_kwargs = {
        k: v for k, v in slurm_client_kwargs.items() if k != "pre_script"
    }
    return SlurmScriptRestClient(**slurm_client_kwargs)


def test_script(slurm_script_client, slurm_parameters):
    nbefore = len(list(slurm_script_client.get_all_job_properties(update_time=None)))
    job_id = slurm_script_client.submit_script(_SUCCESS_SCRIPT)
    try:
        try:
            assert slurm_script_client.wait_finished(job_id, timeout=60) == "COMPLETED"
        finally:
            slurm_script_client.print_stdout_stderr(job_id)

        assert slurm_script_client.get_status(job_id) == "COMPLETED"
        nafter = len(list(slurm_script_client.get_all_job_properties(update_time=None)))
        if slurm_parameters["mock"]:
            # This might fail on a production SLURM queue
            assert (nafter - nbefore) == 1
    finally:
        slurm_script_client.clean_job_artifacts(job_id)


def test_failing_script(slurm_script_client):
    job_id = slurm_script_client.submit_script(_FAIL_SCRIPT)
    try:
        assert slurm_script_client.wait_finished(job_id, timeout=60) == "FAILED"
        slurm_script_client.print_stdout_stderr(job_id)
    finally:
        slurm_script_client.clean_job_artifacts(job_id)


def test_cancel_script(slurm_script_client):
    job_id = slurm_script_client.submit_script(_SUCCESS_SCRIPT)
    try:
        slurm_script_client.cancel_job(job_id)
        assert slurm_script_client.wait_finished(job_id, timeout=60) == "CANCELLED"
        slurm_script_client.print_stdout_stderr(job_id)
    finally:
        slurm_script_client.clean_job_artifacts(job_id)


def test_script_parameters(slurm_script_client):
    parameters = {"time_limit": "00:05:00", "environment": {"NAME1": "VAR1"}}
    metadata = {"NAME2": "VAR2"}
    job_id = slurm_script_client.submit_script(
        _SUCCESS_SCRIPT, parameters=parameters, metadata=metadata
    )
    try:
        try:
            assert slurm_script_client.wait_finished(job_id, timeout=60) == "COMPLETED"
        finally:
            slurm_script_client.print_stdout_stderr(job_id)

        assert slurm_script_client.get_status(job_id) == "COMPLETED"
        properties = slurm_script_client.get_job_properties(job_id)
    finally:
        slurm_script_client.clean_job_artifacts(job_id)

    assert properties.comment == '{"NAME2": "VAR2"}'
    assert properties.time_limit.model_dump() == {
        "infinite": False,
        "number": 5,
        "set": True,
    }


_SUCCESS_SCRIPT = """
echo 'Job started'
echo 'Job finished'
"""

_FAIL_SCRIPT = """
echo 'Job started'
exit 3
"""
