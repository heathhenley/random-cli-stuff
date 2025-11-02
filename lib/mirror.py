import argparse
import pathlib
import shutil
import logging

from lib.base_handler import CmdResult


def add_mirror_subcommand(subparsers: argparse._SubParsersAction) -> None:
    mirror_parser = subparsers.add_parser(
        "mirror",
        help="Mirror a Google Share folder to a local folder",
        description=(
            "Mirror Google Share folder to a local folder. Made for when the "
            "web UI fails to download large folders, and I don't want to let "
            "whole drive sync."
        ),
    )
    mirror_parser.add_argument(
        "--share-folder",
        type=str,
        required=True,
        help="The Google Share folder to pull down",
    )
    mirror_parser.add_argument(
        "--local-folder",
        type=str,
        required=True,
        help="The local folder to mirror the share folder to",
    )
    mirror_parser.add_argument(
        "--exists-ok",
        action="store_true",
        help="If the destination folder already exists, do not raise an error",
    )
    mirror_parser.set_defaults(handler=handle_mirror_command)


def handle_mirror_command(args: argparse.Namespace) -> CmdResult:
    src = pathlib.Path(args.share_folder)
    if not src.exists():
        logging.error(f"Source folder not found: {src}")
        return {
            "results": None,
            "exit_code": 1,
        }
    dst = pathlib.Path(args.local_folder)
    try:
        shutil.copytree(src, dst, dirs_exist_ok=args.exists_ok)
    except FileExistsError:
        logging.error(f"Destination folder already exists: {dst}")
        return {
            "results": None,
            "exit_code": 1,
        }
    except Exception as e:
        logging.error(f"Error copying folder: {e}")
        return {
            "results": None,
            "exit_code": 1,
        }
    return {
        "results": None,
        "exit_code": 0,
    }
