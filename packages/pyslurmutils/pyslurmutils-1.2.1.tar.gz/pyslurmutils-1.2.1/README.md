# pyslurmutils

SLURM utilities for scheduling jobs from Python.

The main purpose of this library is to provide a `concurrent.futures.Executor`
implementation for SLURM which can be used on any machine, not necessarily a SLURM client.

```bash
pip install pyslurmutils
```

```python
from pyslurmutils.concurrent.futures import SlurmRestExecutor

with SlurmRestExecutor(
    url=url,                               # SLURM REST URL
    user_name=user_name,                   # SLURM user name
    token=token,                           # SLURM access token
    log_directory="/path/to/log",          # for log files (optional)
    data_directory="/path/to/data",        # TCP communication when not provided
    pre_script="module load ewoks",        # load environment (optional)
    parameters={"time_limit": "02:00:00"}, # SLURM job parameters (optional)
    python_cmd="python",                   # python command (python3 by default)
) as executor:
    future = executor.submit(sum, [1, 1])
    assert future.result() == 2
```

## Documentation

https://pyslurmutils.readthedocs.io/
