"""Find the args used by the main CLI."""

import argparse

from .data.league import League
from .loglevel import LogLevel

STDOUT_FILE = "-"


def parse_args() -> argparse.Namespace:
    """Create the args based on the CLI inputs."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--league",
        choices=list(League),
        help="The league to fetch data for.",
    )
    parser.add_argument(
        "--loglevel",
        default=LogLevel.INFO,
        choices=list(LogLevel),
        help="The loglevel to display logs at..",
        required=False,
    )
    parser.add_argument(
        "--leaguemodel",
        required=False,
        help="The league model to use.",
    )
    parser.add_argument(
        "--timeout",
        required=False,
        help="The timeout to use (in seconds).",
        type=int,
    )
    parser.add_argument(
        "file",
        default=STDOUT_FILE,
        help="The file to write the output to (- if to stdout).",
    )
    return parser.parse_args()
