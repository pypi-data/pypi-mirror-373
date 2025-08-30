import time
import threading

from concurrent.futures import as_completed
from ..client.job_io.local._executor import RemoteExecutor


def test_remote_executor_nomax():
    # All tasks are executed sequentially (time = ntasks * sleep)
    with RemoteExecutor(conservative_scheduling=True) as executor:
        nworkers = _assert_executor(executor, ntasks=10)
        assert nworkers == 1

    # All tasks are executed in parallel (time = sleep)
    with RemoteExecutor() as executor:
        nworkers = _assert_executor(executor, ntasks=10)
        assert nworkers == 10

    # Sequential blocks of `max_tasks_per_worker tasks` (time = max_tasks_per_worker * sleep)
    with RemoteExecutor(
        max_tasks_per_worker=3, conservative_scheduling=True
    ) as executor:
        nworkers = _assert_executor(executor, ntasks=10)
        assert nworkers == 4

    # All tasks are executed in parallel (time = sleep)
    with RemoteExecutor(max_tasks_per_worker=1) as executor:
        nworkers = _assert_executor(executor, ntasks=10)
        assert nworkers == 10


def test_remote_executor_max():
    # Tasks executed in parallel blocks of `max_workers` (time = ceil(ntasks/max_workers) * sleep)
    with RemoteExecutor(max_workers=3) as executor:
        nworkers = _assert_executor(executor, ntasks=10)
        assert nworkers == 3

    # Tasks executed in parallel blocks of `max_workers` (time = ceil(ntasks/max_workers) * sleep)
    with RemoteExecutor(max_workers=3, max_tasks_per_worker=2) as executor:
        nworkers = _assert_executor(executor, ntasks=10)
        assert nworkers > 3

    # Tasks executed in parallel blocks of `max_workers` (time = ceil(ntasks/max_workers) * sleep)
    with RemoteExecutor(
        max_workers=3, max_tasks_per_worker=2, lazy_scheduling=False
    ) as executor:
        nworkers = _assert_executor(executor, ntasks=10)
        assert nworkers > 3


def _assert_executor(executor, ntasks, sleep=0.1) -> int:
    futures_list = []
    data = list(range(ntasks))
    for i in data:
        future = executor.submit(_example_task, i, sleep=sleep)
        futures_list.append(future)

    results = list()
    thread_ids = set()
    for future in as_completed(futures_list):
        i, thread_id = future.result()
        results.append(i)
        thread_ids.add(thread_id)

    assert data == sorted(results)
    return len(thread_ids)


def _example_task(i, sleep=0.1):
    time.sleep(sleep)
    return i, id(threading.current_thread())
