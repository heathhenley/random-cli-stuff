import argparse
import csv
from collections import namedtuple
import hashlib
import pathlib
import logging

from lib.base_handler import CmdResult

ACCEPTABLE_IMAGE_EXTENSIONS = (".jpg", ".jpeg")


def format_size(size: int) -> str:
    if size < 1024:
        return f"{size} bytes"
    if size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    if size < 1024 * 1024 * 1024:
        return f"{size / 1024 / 1024:.2f} MB"
    return f"{size / 1024 / 1024 / 1024:.2f} GB"


def hash_file(file: pathlib.Path, chunk_size: int = 4096) -> str:
    """Hash a file using SHA-256"""
    hasher = hashlib.sha256()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def add_analyze_subcommand(subparsers: argparse._SubParsersAction) -> None:
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a directory tree - counts files, duplicates, and total size.",
        description="Analyze a directory tree, walk through and count files, number of duplicates, etc. "
        "Optionally save the file index to a file for later use.",
    )
    analyze_parser.add_argument(
        "--directory",
        type=str,
        required=True,
        help="The directory to analyze",
    )
    analyze_parser.add_argument(
        "--output-file",
        type=str,
        required=False,
        default=None,
        help=(
            "The file to save the file index to - it's a csv file with path "
            "and hash as the columns."
        ),
    )
    analyze_parser.add_argument(
        "--extensions",
        type=str,
        nargs="*",
        required=False,
        default=list(ACCEPTABLE_IMAGE_EXTENSIONS),
        help="The extensions to consider in the count (default: jpg, jpeg) - case insensitive and the dot is optional.",
    )
    analyze_parser.add_argument(
        "--only-dump-duplicates",
        action="store_true",
        help="Only dump the duplicates to the output file, not the full analysis "
        "- useful for large directories, if you only care about the duplicates.",
        default=False,
    )
    analyze_parser.set_defaults(handler=handle_analyze_command)


ProcessFileResult = namedtuple(
    "ProcessFileResult", ["success", "size", "hash", "error"]
)


def process_file(file: pathlib.Path, extensions: set[str]) -> ProcessFileResult:
    if not file.is_file():
        return ProcessFileResult(success=False, size=0, hash=None, error="Not a file")
    if file.suffix.lower().replace(".", "") not in extensions:
        return ProcessFileResult(
            success=False,
            size=0,
            hash=None,
            error=f"Not an image: {file.suffix.lower().replace('.', '')} (not in extensions: {extensions})",
        )
    return ProcessFileResult(
        success=True, size=file.stat().st_size, hash=hash_file(file), error=None
    )


def _dedup_maybe(
    duplicates: dict[str, list[str]], only_dump_duplicates: bool
) -> dict[str, list[str]]:
    if not only_dump_duplicates:
        return duplicates
    return {hash: files for hash, files in duplicates.items() if len(files) > 1}


def write_data_file(file: str, data: dict[str, list[str]]) -> bool:
    try:
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["path", "hash"])
            for hash, files in data.items():
                for file in files:
                    writer.writerow([file, hash])
        return True
    except Exception as e:
        logging.error(f"Error writing data file: {e}")
        return False


def handle_analyze_command(args: argparse.Namespace) -> CmdResult:
    logging.info(f"Analyzing directory: {args.directory}")
    logging.info(f"Including extensions: {args.extensions}")
    if args.output_file is not None:
        logging.info(f"Saving file index to: {args.output_file}")
        if args.only_dump_duplicates:
            logging.info(
                "  Only dumping duplicates to the output file, not the full analysis"
            )

    directory = pathlib.Path(args.directory)
    if not directory.exists():
        logging.error(f"Directory not found: {directory}")
        return {
            "results": None,
            "exit_code": 1,
        }

    total_images = 0
    total_size = 0
    duplicates = {}  # hash -> list of files
    extensions = set([ext.lower().replace(".", "") for ext in args.extensions])

    for file in directory.glob("**/*"):
        logging.debug(f"Analyzing file: {file}")

        result = process_file(file, extensions)

        if not result.success:
            logging.debug(f"Skipping file: {file} ({result.error})")
            continue

        total_images += 1
        total_size += result.size
        hash = result.hash
        logging.debug(f"Image: {file}, size: {result.size}, hash: {hash}")
        if total_images % 1000 == 0:
            logging.info(
                f"  Total: {total_images} images,  unique: {len(duplicates)} images, total size: {format_size(total_size)}"
            )
        if hash in duplicates:
            duplicates[hash].append(str(file.relative_to(directory)))
        else:
            duplicates[hash] = [str(file.relative_to(directory))]

    logging.info(f"Total images: {total_images}")
    logging.info(f"Unique images: {len(duplicates)}")
    logging.info(f"Duplicates: {total_images - len(duplicates)}")
    logging.info(f"Total size: {format_size(total_size)}")

    if args.output_file is not None:
        data_to_write = _dedup_maybe(duplicates, args.only_dump_duplicates)
        if not write_data_file(args.output_file, data_to_write):
            logging.error(f"Error writing data file: {args.output_file}")
            return {
                "results": None,
                "exit_code": 1,
            }

    return {
        "results": {
            "total_images": total_images,
            "total_unique": len(duplicates),
            "total_duplicates": total_images - len(duplicates),
            "total_size": format_size(total_size),
        },
        "additional_results": {
            "files_by_hash": duplicates,  # hash -> list of files
        },
        "exit_code": 0,
    }
