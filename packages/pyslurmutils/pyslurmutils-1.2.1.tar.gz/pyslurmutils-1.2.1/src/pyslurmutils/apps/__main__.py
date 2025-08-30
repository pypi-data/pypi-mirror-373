"""Monitor SLURM jobs and status"""

import sys
import time
import argparse
import datetime
import logging

from tabulate import tabulate
from pydantic import BaseModel

from .cli import common as common_cli
from .cli import status as status_cli
from .cli import cancel as cancel_cli
from .cli import submit as submit_cli
from .cli import diff as diff_cli
from ..client import defaults
from ..client import SlurmScriptRestClient
from ..client.rest.api import slurm_response


logger = logging.getLogger(__name__)


def create_argument_parser():
    parser = argparse.ArgumentParser(
        description="SLURM Job Monitor", prog="pyslurmutils"
    )
    subparsers = parser.add_subparsers(help="Commands", dest="command")

    check = subparsers.add_parser("check", help="Check Slurm connection")
    common_cli.add_parameters(check)

    subparser = subparsers.add_parser("status", help="Job status")
    common_cli.add_parameters(subparser)
    status_cli.add_parameters(subparser)

    subparser = subparsers.add_parser("diff", help="Difference between two jobs")
    common_cli.add_parameters(subparser)
    diff_cli.add_parameters(subparser)

    subparser = subparsers.add_parser("cancel", help="Cancel jobs")
    common_cli.add_parameters(subparser)
    cancel_cli.add_parameters(subparser)

    subparser = subparsers.add_parser("submit", help="Submit job")
    common_cli.add_parameters(subparser)
    submit_cli.add_parameters(subparser)

    subparser = subparsers.add_parser("version", help="Slurm API version")
    common_cli.add_parameters(subparser)

    return parser


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = create_argument_parser()

    args = parser.parse_args(argv[1:])

    if args.command == "status":
        command_status(args)
    elif args.command == "diff":
        command_diff(args)
    elif args.command == "check":
        command_check(args)
    elif args.command == "cancel":
        command_cancel(args)
    elif args.command == "submit":
        command_submit(args)
    elif args.command == "version":
        command_version(args)
    else:
        parser.print_help()
    return 0


def command_status(args):
    common_cli.apply_parameters(args)
    status_cli.apply_parameters(args)

    client = SlurmScriptRestClient(
        url=args.url,
        user_name=args.user_name,
        token=args.token,
        api_version=args.api_version,
        renewal_url=args.renewal_url,
        log_directory=args.log_directory,
    )
    for _ in _monitor_loop(args.interval):
        _print_jobs(client, args.jobid, args.all)
        if args.jobid:
            client.print_stdout_stderr(args.jobid)


def command_diff(args):
    common_cli.apply_parameters(args)
    diff_cli.apply_parameters(args)

    client = SlurmScriptRestClient(
        url=args.url,
        user_name=args.user_name,
        token=args.token,
        api_version=args.api_version,
        renewal_url=args.renewal_url,
        log_directory=args.log_directory,
    )

    _diff_jobs(client, args.jobid1, args.jobid2)


def command_check(args):
    common_cli.apply_parameters(args)
    client = SlurmScriptRestClient(
        url=args.url,
        user_name=args.user_name,
        token=args.token,
        api_version=args.api_version,
        renewal_url=args.renewal_url,
        log_directory=args.log_directory,
    )
    has_api, selected_api, versions = client.server_has_api()
    print(f"Selected SLURM API {selected_api}")
    print(f"Server supports {', '.join(versions)}")
    if has_api:
        print("OK!")
    else:
        raise RuntimeError(f"SLURM API {selected_api} is not supported by the server!")


def command_cancel(args):
    common_cli.apply_parameters(args)
    cancel_cli.apply_parameters(args)
    client = SlurmScriptRestClient(
        url=args.url,
        user_name=args.user_name,
        token=args.token,
        api_version=args.api_version,
        renewal_url=args.renewal_url,
        log_directory=args.log_directory,
    )
    job_ids = args.job_ids
    if not job_ids:
        job_ids = [prop["job_id"] for prop in client.get_all_job_properties()]
    for job_id in job_ids:
        client.cancel_job(job_id)


def command_submit(args):
    common_cli.apply_parameters(args)
    submit_cli.apply_parameters(args)
    client = SlurmScriptRestClient(
        url=args.url,
        user_name=args.user_name,
        token=args.token,
        api_version=args.api_version,
        renewal_url=args.renewal_url,
        parameters=args.parameters,
        log_directory=args.log_directory,
    )
    job_id = client.submit_script(args.script)
    print(f"SLURM job {job_id} started")
    if not args.wait:
        return
    try:
        client.wait_finished(job_id)
        client.print_stdout_stderr(job_id)
    finally:
        client.clean_job_artifacts(job_id)


def command_version(args):
    common_cli.apply_parameters(args)
    client = SlurmScriptRestClient(
        url=args.url,
        user_name=args.user_name,
        token=args.token,
        api_version=args.api_version,
        renewal_url=args.renewal_url,
    )
    print(f"Default SLURM API {defaults.DEFAULT_API_VERSION}")
    print(f"Selected SLURM API {client._api_version_str}")


def _monitor_loop(interval):
    try:
        if not interval:
            yield
            return
        while True:
            yield
            time.sleep(interval)
    except KeyboardInterrupt:
        pass


def _print_jobs(client, jobid, all_users):
    if jobid:
        jobs = [client.get_job_properties(jobid)]
    else:
        jobs = client.get_all_job_properties(all_users=all_users)

    columns = {
        "ID": (_as_str, ("job_id",)),
        "Name": (_as_str, ("name", 30)),
        "State": (_job_state, ()),
        "User": (_as_str, ("user_name",)),
        "Limit": (_as_minutes, ("time_limit",)),
        "Submit": (_as_timestamp, ("submit_time",)),
        "Pendtime": (_time_diff, ("submit_time", "start_time", False)),
        "Runtime": (_time_diff, ("start_time", "end_time", True)),
        "Resources": (_resources, ("partition", "tres_req_str", "tres_alloc_str")),
    }

    rows = list()
    for job_properties in jobs:
        rows.append(
            [
                parser(job_properties, *parser_args)
                for parser, parser_args in columns.values()
            ]
        )
    if not rows:
        print("No jobs found!")
        return
    titles = list(columns)
    table = tabulate(rows, headers=titles)
    print(table)


def _as_str(job_properties: BaseModel, key: str, max_len: int = None) -> str:
    string = str(getattr(job_properties, key, "-"))
    if not max_len or len(string) <= max_len:
        return string
    return string[: max_len - 3] + "..."


def _job_state(job_properties: BaseModel) -> str:
    return slurm_response.slurm_job_state(job_properties)


def _resources(
    job_properties: BaseModel, partition: str, requested: str, allocated: str
) -> str:
    partition = getattr(job_properties, partition, None)
    requested = getattr(job_properties, requested, None)
    allocated = getattr(job_properties, allocated, None)
    return f"{partition}: {requested or allocated}"


def _as_timestamp(job_properties: BaseModel, epoch: str) -> datetime.datetime:
    epoch = getattr(job_properties, epoch, None)
    return slurm_response.slurm_unix_timestamp_or_now(epoch)


def _as_minutes(job_properties: BaseModel, minutes: str) -> datetime.timedelta:
    minutes = getattr(job_properties, minutes, None)
    return slurm_response.slurm_duration_minutes(minutes)


def _time_diff(
    job_properties: BaseModel, start_time: str, end_time: str, check_state: bool
) -> str:
    start_time = getattr(job_properties, start_time, None)
    end_time = getattr(job_properties, end_time, None)

    if check_state:
        state = slurm_response.slurm_job_state(job_properties)
        if state == "PENDING":
            return "-"
        if state not in slurm_response.FINISHING_STATES:
            end_time = None

    start_time = slurm_response.slurm_unix_timestamp_or_now(start_time)
    end_time = slurm_response.slurm_unix_timestamp_or_now(end_time)
    duration = end_time - start_time
    if duration.total_seconds() < 0:
        return "-"
    return str(duration)


def _diff_jobs(client, jobid1: int, jobid2: int):
    job1 = client.get_job_properties(jobid1)
    job2 = client.get_job_properties(jobid2)

    diffs = _recursive_diff(job1.model_dump(), job2.model_dump())

    if diffs:
        rows = [
            (path, _truncate_table_value(v1, 60), _truncate_table_value(v2, 60))
            for path, (v1, v2) in diffs.items()
        ]
        print(tabulate(rows, headers=["Path", "Job 1", "Job 2"], tablefmt="fancy_grid"))
    else:
        print("Jobs are identical!")


def _truncate_table_value(value, width: int) -> str:
    s = str(value)
    if len(s) <= width:
        return s
    return s[: width - 3] + "..."


def _recursive_diff(d1, d2, path=""):
    diffs = {}

    if isinstance(d1, dict) and isinstance(d2, dict):
        all_keys = set(d1) | set(d2)
        for key in all_keys:
            v1 = d1.get(key, "<MISSING>")
            v2 = d2.get(key, "<MISSING>")
            current_path = f"{path}.{key}" if path else key
            diffs.update(_recursive_diff(v1, v2, current_path))

    elif isinstance(d1, list) and isinstance(d2, list):
        try:
            d1 = sorted(d1)
            d2 = sorted(d2)
        except Exception:
            pass
        max_len = max(len(d1), len(d2))
        for i in range(max_len):
            v1 = d1[i] if i < len(d1) else "<MISSING>"
            v2 = d2[i] if i < len(d2) else "<MISSING>"
            current_path = f"{path}[{i}]"
            if isinstance(v1, (dict, list)) and isinstance(v2, (dict, list)):
                diffs.update(_recursive_diff(v1, v2, current_path))
            elif v1 != v2:
                diffs[current_path] = (v1, v2)

    elif d1 != d2:
        diffs[path] = (d1, d2)

    return diffs


if __name__ == "__main__":
    sys.exit(main())
