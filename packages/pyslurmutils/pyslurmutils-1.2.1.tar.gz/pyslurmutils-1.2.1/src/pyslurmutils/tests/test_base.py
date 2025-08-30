import pytest
from ..client import SlurmBaseRestClient
from ..client.errors import RemoteHttpError


@pytest.fixture
def slurm_base_client(slurm_client_kwargs) -> SlurmBaseRestClient:
    slurm_client_kwargs = {
        k: v for k, v in slurm_client_kwargs.items() if k != "pre_script"
    }
    return SlurmBaseRestClient(**slurm_client_kwargs)


def test_version(slurm_base_client):
    assert slurm_base_client.server_has_api()


def test_wrong_job_wait(slurm_base_client):
    job_id = 0
    with pytest.raises(RemoteHttpError):
        slurm_base_client.wait_finished(job_id)


def test_wrong_job_print(slurm_base_client):
    job_id = 0
    slurm_base_client.print_stdout_stderr(job_id)


def test_wrong_job_clean(slurm_base_client):
    job_id = 0
    slurm_base_client.clean_job_artifacts(job_id)
