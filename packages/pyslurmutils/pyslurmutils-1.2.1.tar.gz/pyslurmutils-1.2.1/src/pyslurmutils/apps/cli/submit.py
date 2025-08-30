import json
from typing import Tuple, Any


def add_parameters(parser):
    parser.add_argument(
        "script",
        nargs="*",
        type=str,
        default=["echo This is a test"],
        help="Inline script",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="All jobs when no job ID is provided",
    )
    parser.add_argument(
        "-sp",
        "--slurm-parameter",
        dest="parameters",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="SLURM parameters",
    )
    parser.add_argument(
        "-w",
        "--wait",
        action="store_true",
        help="Wait until the job is finished",
    )


def apply_parameters(args):
    args.parameters = dict(parse_parameter(p) for p in args.parameters)


def parse_parameter(option: str) -> Tuple[str, Any]:
    option, _, value = option.partition("=")
    return option, parse_value(value)


def parse_value(value: str) -> Any:
    try:
        return json.loads(value)
    except Exception:
        return value
