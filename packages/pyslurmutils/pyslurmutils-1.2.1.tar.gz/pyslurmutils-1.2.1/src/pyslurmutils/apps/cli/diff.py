def add_parameters(parser):
    parser.add_argument(
        "jobid1",
        type=str,
        help="SLURM Job ID",
    )
    parser.add_argument(
        "jobid2",
        type=str,
        help="SLURM Job ID",
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
