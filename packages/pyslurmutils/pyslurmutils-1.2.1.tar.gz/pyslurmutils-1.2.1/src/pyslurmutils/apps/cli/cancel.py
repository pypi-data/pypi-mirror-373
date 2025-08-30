def add_parameters(parser):
    parser.add_argument(
        "job_ids",
        nargs="*",
        type=int,
        default=0,
        help="SLURM Job ID's to be cancelled",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="All jobs when no job ID is provided",
    )


def apply_parameters(args):
    pass
