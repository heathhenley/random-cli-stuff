"""
Collection of random cmd line tools / scripts.

If it makes it here it probably started as an actual one-off, and then I needed
to use it again in a more general way so I added it here. They're all
subcommands of the main cli tool at the moment - get help on any subcommand
with `uv run main.py <command> --help` or list all subcommands with `uv run main.py --help`.
"""

import argparse
import json
import logging

from lib import mirror
from lib import analyze

from lib.base_handler import HandlerCmdType


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="one-offs", description=__doc__, usage="%(prog)s [options] <command>"
    )
    parser.add_argument(
        "--verbosity", "-v", action="count", default=0, help="Increase verbosity"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    mirror.add_mirror_subcommand(subparsers)
    analyze.add_analyze_subcommand(subparsers)
    return parser


LOG_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(level=LOG_LEVELS[args.verbosity])

    handler: HandlerCmdType | None = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 2

    result = handler(args)
    if result["results"] is not None:
        print(json.dumps(result["results"], indent=2))
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
