# Copyright (C) 2023,2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""A console program that generates yearly calendar heatmap.

website: https://github.com/kianmeng/heatmap_cli
changelog: https://github.com/kianmeng/heatmap_cli/blob/master/CHANGELOG.md
issues: https://github.com/kianmeng/heatmap_cli/issues
"""

import argparse
import datetime
import logging
import multiprocessing
import sys
from itertools import zip_longest
from typing import Optional, Sequence

import matplotlib.pyplot as plt

from heatmap_cli import (
    DemoAction,
    EnvironmentAction,
    __version__,
    setup_logging,
)
from heatmap_cli.heatmap import run as generate_heatmaps

IMAGE_FORMATS = [
    "eps",
    "jpeg",
    "jpg",
    "pdf",
    "pgf",
    "png",
    "ps",
    "raw",
    "rgba",
    "svg",
    "svgz",
    "tif",
    "tiff",
    "webp",
]


# Suppress logging from matplotlib in debug mode.
logging.getLogger("matplotlib").propagate = False
logger = multiprocessing.get_logger()

# Sort colormaps in a case-insensitive manner.
CMAPS = sorted(plt.colormaps, key=str.casefold)
DEFAULT_CMAP = "RdYlGn_r"


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="heatmap_cli",
        add_help=False,
        description=__doc__,
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(
            prog,
            max_help_position=6,
        ),
    )

    parser.add_argument(
        "--demo",
        const=len(CMAPS),
        action=DemoAction,
        type=int,
        dest="demo",
        help=(
            "generate number of heatmaps by colormaps "
            f"(default: '{len(CMAPS)}')"
        ),
        metavar="NUMBER_OF_COLORMAP",
    )

    parser.add_argument(
        "-y",
        "--year",
        dest="year",
        type=int,
        default=datetime.datetime.today().year,
        help="filter by year from the CSV file (default: '%(default)s')",
        metavar="YEAR",
    )

    parser.add_argument(
        "-w",
        "--week",
        dest="week",
        type=int,
        default=datetime.datetime.today().isocalendar().week,
        help=(
            "filter until week of the year from the CSV file "
            "(default: '%(default)s')"
        ),
        metavar="WEEK",
    )

    parser.add_argument(
        "-e",
        "--end-date",
        dest="end_date",
        default=None,
        help=(
            "filter until the date of the year from the CSV file and "
            "this will overwrite -y and -w option (default: %(default)s)"
        ),
        metavar="END_DATE",
    )

    parser.add_argument(
        "-O",
        "--output-dir",
        dest="output_dir",
        default="output",
        help="set default output folder (default: '%(default)s')",
    )

    parser.add_argument(
        "-o",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help=(
            "open the generated heatmap using the default program "
            "(default: %(default)s)"
        ),
    )

    parser.add_argument(
        "-p",
        "--purge",
        default=False,
        action="store_true",
        dest="purge",
        help=(
            "remove all leftover artifacts set by "
            "--output-dir folder (default: %(default)s)"
        ),
    )

    parser.add_argument(
        "-v",
        "--verbose",
        default=0,
        action="count",
        dest="verbose",
        help="show verbosity of debugging log. Use -vv, -vvv for more details",
    )

    parser.add_argument(
        "input_filename",
        help="CSV filename (required unless --demo is used)",
        type=str,
        metavar="CSV_FILENAME",
        nargs="?",  # Always optional in parser, checked later in main()
        default=None,
    )

    parser.add_argument(
        "-t",
        "--title",
        dest="title",
        default=None,
        help="set title for the heatmap (default: %(default)s)",
    )

    parser.add_argument(
        "-u",
        "--author",
        dest="author",
        default="kianmeng.org",
        help="set author for the heatmap (default: %(default)s)",
    )

    parser.add_argument(
        "-f",
        "--format",
        dest="format",
        choices=IMAGE_FORMATS,
        default="png",
        help="set the default image format (default: '%(default)s')",
        metavar="IMAGE_FORMAT",
    )

    parser.add_argument(
        "-c",
        "--cmap",
        choices=plt.colormaps,
        dest="cmap",
        default=None,  # Default is handled in main()
        action="append",
        help=_generate_cmap_help(),
        metavar="COLORMAP",
    )

    parser.add_argument(
        "-i",
        "--cmap-min",
        dest="cmap_min",
        type=float,
        default=None,
        help=(
            "Set the minimum value of the colormap range "
            "(default: %(default)s)"
        ),
        metavar="COLORMAP_MIN_VALUE",
    )

    parser.add_argument(
        "-x",
        "--cmap-max",
        dest="cmap_max",
        type=float,
        default=None,
        help=(
            "Set the maximum value of the colormap range "
            "(default: %(default)s)"
        ),
        metavar="COLORMAP_MAX_VALUE",
    )

    parser.add_argument(
        "-b",
        "--cbar",
        default=False,
        action="store_true",
        dest="cbar",
        help="show colorbar (default: %(default)s)",
    )

    parser.add_argument(
        "-a",
        "--annotate",
        default=True,
        action=argparse.BooleanOptionalAction,
        dest="annotate",
        help="add count to each heatmap region",
    )

    parser.add_argument(
        "--animate-by-week",
        default=False,
        action="store_true",
        dest="animate_by_week",
        help="create an animation for each day of the current week",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        default=False,
        action="store_true",
        dest="quiet",
        help="suppress all logging",
    )

    parser.add_argument(
        "-Y",
        "--yes",
        default=False,
        action="store_true",
        dest="yes",
        help="yes to prompt",
    )

    parser.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        dest="debug",
        help="show debugging log and stack trace",
    )

    parser.add_argument(
        "-E",
        "--env",
        action=EnvironmentAction,
        dest="env",
        help="print environment information for bug reporting",
    )

    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="show this help message and exit.",
    )

    return parser


def _generate_cmap_help() -> str:
    """Generate the help text for colormap options.

    Returns:
        str: Formatted help text.
    """
    cmap_help = "Set default colormap."
    cmap_default = f" (default: '{DEFAULT_CMAP}')"

    # Always show all colormaps in help text
    items_per_row = 6
    cmap_choices = "\nAvailable colormaps:\n"
    cmap_bygroups = zip_longest(*(iter(CMAPS),) * items_per_row)
    for cmap_bygroup in cmap_bygroups:
        cmap_choices += "  " + ", ".join(filter(None, cmap_bygroup)) + "\n"

    return cmap_help + cmap_default + "\n" + cmap_choices.rstrip()


def _process_args(
    parser: argparse.ArgumentParser, parsed_args: argparse.Namespace
) -> argparse.Namespace:
    """Perform post-parsing validation and processing of arguments.

    Args:
        parser (argparse.ArgumentParser): The argument parser instance.
        parsed_args (argparse.Namespace): The initially parsed arguments.

    Returns:
        argparse.Namespace: The validated and processed arguments.

    Raises:
        SystemExit: If validation fails, typically via parser.error().
    """
    # Handle --end-date overriding --year and --week
    if parsed_args.end_date:
        try:
            date = datetime.datetime.strptime(parsed_args.end_date, "%Y-%m-%d")
            (year, week, _day) = date.isocalendar()
            parsed_args.year = year
            parsed_args.week = week
        except ValueError:
            # Use parser.error to exit cleanly with a message
            parser.error(
                f"argument --end-date: invalid date format: "
                f"'{parsed_args.end_date}', expected YYYY-MM-DD."
            )

    # Set default cmap if none provided
    if not parsed_args.cmap:
        parsed_args.cmap = [DEFAULT_CMAP]

    # Check if input_filename is required and missing
    if not parsed_args.demo and parsed_args.input_filename is None:
        parser.error("the following arguments are required: CSV_FILENAME")

    return parsed_args


def main(args: Optional[Sequence[str]] = None) -> None:
    """Run the main program flow.

    Parses arguments, processes them, sets up logging, and runs heatmap
    generation.

    Args:
        args (List | None): Argument passed through the command line.

    Returns:
        None
    """
    args = args if args is not None else sys.argv[1:]
    parser = build_parser()
    # Use parse_known_args to potentially capture debug flag even if other args
    # fail. However, we'll rely on the full parse_args within the try block for
    # simplicity here.
    parsed_args = None
    debug_active = False  # Initialize to False, will be set after parsing

    try:
        parsed_args = parser.parse_args(args)
        debug_active = parsed_args.debug

        processed_args = _process_args(parser, parsed_args)
        setup_logging(processed_args)
        generate_heatmaps(processed_args)

    except Exception as error:
        message = getattr(error, "message", str(error))
        logger.error("error: %s", message, exc_info=debug_active)

        # exit with error code 1, suppressing the original exception traceback
        # unless debug mode is active (handled by logger exc_info).
        raise SystemExit(1) from None
