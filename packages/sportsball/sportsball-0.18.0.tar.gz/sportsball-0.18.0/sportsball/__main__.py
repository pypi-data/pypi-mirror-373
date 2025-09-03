"""The CLI for executing the data harvesting."""

import datetime
import io
import logging
import sys
from contextlib import redirect_stdout

from . import __VERSION__
from .args import parse_args
from .data import league_model
from .data.league import league_from_str
from .logger import setup_logger
from .sportsball import SportsBall

_STDOUT_FILE = "-"


def main() -> None:
    """The main CLI function."""
    with redirect_stdout(sys.stderr):
        args = parse_args()
        setup_logger()

        logging.info("--- sportsball %s ---", __VERSION__)

        if args.timeout is not None:
            league_model.TIMEOUT_DT = datetime.datetime.now() + datetime.timedelta(
                seconds=args.timeout
            )

        ball = SportsBall()
        league = ball.league(league_from_str(args.league), args.leaguemodel)
        df = league.to_frame()
        handle = io.BytesIO()
        df.to_parquet(handle, compression="gzip")
        handle.seek(0)
    if args.file == _STDOUT_FILE:
        sys.stdout.buffer.write(handle.getbuffer())
    else:
        with open(args.file, "wb") as fhandle:
            fhandle.write(handle.getbuffer())


if __name__ == "__main__":
    main()
