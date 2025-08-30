def add_parameters(parser):
    parser.add_argument(
        "-j",
        "--jobid",
        type=int,
        default=0,
        help="SLURM Job ID (all jobs when not provided)",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="All users when '--jobid' is not set",
    )
    parser.add_argument(
        "-m",
        "--monitor",
        dest="interval",
        type=float,
        default=0,
        help="Monitor are intervals of x seconds",
    )


def apply_parameters(args):
    pass
