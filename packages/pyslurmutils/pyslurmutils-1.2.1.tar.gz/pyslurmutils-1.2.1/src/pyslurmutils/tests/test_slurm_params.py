import pytest

from ..client.rest.api.slurm_params import _integral_number
from ..client.rest.api.slurm_params import coerce_parameters


def test_integral_number():
    assert _integral_number((0, 0, 41), 5) == {
        "number": 5,
        "set": True,
        "infinite": False,
    }
    assert _integral_number((0, 0, 41), 5.2) == {
        "number": 5,
        "set": True,
        "infinite": False,
    }
    assert _integral_number((0, 0, 41), 5.5) == {
        "number": 6,
        "set": True,
        "infinite": False,
    }
    assert _integral_number((0, 0, 41), "10") == {
        "number": 10,
        "set": True,
        "infinite": False,
    }
    assert _integral_number((0, 0, 41), "10.6") == {
        "number": 11,
        "set": True,
        "infinite": False,
    }
    assert _integral_number((0, 0, 41), "not-a-number") == "not-a-number"


def test_timedelta_in_minutes():
    parameters = {"time_limit": "01:00:00"}
    expected = {"time_limit": {"number": 60, "set": True, "infinite": False}}
    coerce_parameters((0, 0, 41), parameters)
    assert parameters == expected

    parameters = {"time_limit": 30.6}
    expected = {"time_limit": {"number": 31, "set": True, "infinite": False}}
    coerce_parameters((0, 0, 41), parameters)
    assert parameters == expected

    parameters = {"time_limit": "not-a-time"}
    expected = {"time_limit": "not-a-time"}
    coerce_parameters((0, 0, 41), parameters)
    assert parameters == expected


def test_environment_version():
    parameters = {"environment": {"A": 1, "B": "test"}}
    expected = {"environment": {"A": "1", "B": "test"}}
    coerce_parameters((0, 0, 38), parameters)
    assert parameters == expected

    parameters = {"environment": {"A": 1, "B": "test"}}
    expected = {"environment": ["A=1", "B=test"]}
    coerce_parameters((0, 0, 41), parameters)
    assert parameters == expected


@pytest.mark.parametrize(
    "mem, int_mb",
    [
        ("1G", 1024),
        ("1GB", 1024),
        ("0.5GB", 512),
        ("512M", 512),
        ("100K", 1),
        ("2048", 2048),
        (2048.2, 2048),
    ],
)
def test_memory_in_megabytes(mem, int_mb):
    parameters = {"memory_per_cpu": mem}
    expected = {"memory_per_cpu": {"number": int_mb, "set": True, "infinite": False}}
    coerce_parameters((0, 0, 41), parameters)
    assert parameters == expected


def test_tres_memory_in_megabytes():
    parameters = {"memory_per_tres": "gres/gpu:2G; gres/mic:512M"}
    expected = {"memory_per_tres": "gres/gpu:2048;gres/mic:512"}
    coerce_parameters((0, 0, 41), parameters)
    assert parameters == expected

    parameters = {"memory_per_tres": "gres/gpu:1G;gres/gpu:512M"}
    expected = {"memory_per_tres": "gres/gpu:1536"}
    coerce_parameters((0, 0, 41), parameters)
    assert parameters == expected

    parameters = {"memory_per_tres": "invalid_format"}
    expected = {"memory_per_tres": "invalid_format"}
    coerce_parameters((0, 0, 41), parameters)
    assert parameters == expected
