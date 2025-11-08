import argparse
import pathlib
import shutil
import logging

from lib.base_handler import CmdResult


def add_copy_tree_subcommand(subparsers: argparse._SubParsersAction) -> None:
    copy_tree_parser = subparsers.add_parser(
        "copy_tree",
        help="Copy a tree of files from one location to another. Like a bad "
        "version of robocopy, except I have more control to hack on files if needed.",
        description=(
            "Copy a tree of files from one location to another. Like a bad "
            "version of robocopy, except I have more control if needed here."
        ),
    )
    copy_tree_parser.add_argument(
        "--source-folder",
        type=str,
        required=True,
        help="The source folder to copy from",
    )
    copy_tree_parser.add_argument(
        "--destination-folder",
        type=str,
        required=True,
        help="The destination folder to copy to",
    )
    copy_tree_parser.add_argument(
        "--exists-ok",
        action="store_true",
        help="If the destination folder already exists, do not raise an error",
    )
    copy_tree_parser.set_defaults(handler=handle_copy_tree_command)


def handle_copy_tree_command(args: argparse.Namespace) -> CmdResult:
    src = pathlib.Path(args.source_folder)
    if not src.exists():
        logging.error(f"Source folder not found: {src}")
        return {
            "results": None,
            "exit_code": 1,
        }
    dst = pathlib.Path(args.destination_folder)
    try:
        shutil.copytree(src, dst, dirs_exist_ok=args.exists_ok)
    except FileExistsError:
        logging.error(f"Destination folder already exists: {dst}")
        return {
            "results": None,
            "exit_code": 1,
        }
    except Exception as e:
        logging.error(f"Error copying tree: {e}")
        return {
            "results": None,
            "exit_code": 1,
        }
    return {
        "results": None,
        "exit_code": 0,
    }
