# Copyright (C) 2023,2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# pylint: disable=W0622,R0903

"""A console program that generates a yearly calendar heatmap."""

import argparse
import datetime
import logging
import multiprocessing
import platform
import random
import sys
from importlib import metadata
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from heatmap_cli.heatmap import run as generate_heatmaps

__version__ = metadata.version("heatmap_cli")

# Max value for demo heatmap count
DEMO_MAX_COUNT = 12000

# Sort colormaps in a case-insensitive manner.
CMAPS = sorted(plt.colormaps, key=str.casefold)

# Suppress logging from matplotlib in debug mode.
logging.getLogger("matplotlib").propagate = False
logger = multiprocessing.get_logger()


def setup_logging(config: argparse.Namespace) -> None:
    """Set up logging by level.

    Args:
        config (argparse.Namespace): Config from arguments.

    Returns:
        None
    """
    if config.quiet:
        logging.disable(logging.NOTSET)
        return

    level = logging.DEBUG if config.debug else logging.INFO
    format_string = (
        "[%(asctime)s] %(levelname)s: %(name)s: %(message)s"
        if config.debug
        else "%(message)s"
    )

    logger.setLevel(level)
    formatter = logging.Formatter(format_string)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if not config.debug:
        logger.addFilter(
            lambda record: not record.getMessage().startswith(
                ("child", "process")
            )
        )


class DemoAction(argparse.Action):
    """Generate a list of demo heatmaps action."""

    def __init__(self, *nargs, **kwargs):
        """Overwrite class method."""
        kwargs.update({"nargs": "?"})
        super().__init__(*nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Overwrite class method."""
        setattr(
            namespace, "input_filename", f"{namespace.output_dir}/sample.csv"
        )
        setattr(namespace, "year", datetime.datetime.today().year)
        setattr(namespace, "week", 52)
        setattr(namespace, "demo", values)
        setattr(namespace, "annotate", True)
        setattr(namespace, "cbar", True)
        setattr(namespace, "cmap", random.sample(CMAPS, values))
        setattr(namespace, "cmap_min", False)
        setattr(namespace, "cmap_max", False)
        setattr(namespace, "format", "png")
        setattr(namespace, "title", False)
        setattr(namespace, "debug", True)
        setattr(namespace, "quiet", False)
        setattr(namespace, "purge", True)
        setattr(namespace, "yes", False)

        self._generate_sample_csv(namespace)
        setup_logging(namespace)
        generate_heatmaps(namespace)
        parser.exit()

    def _generate_sample_csv(self, config: argparse.Namespace) -> None:
        """Generate a sample CSV data file.

        Args:
            config (argparse.Namespace): Config from command line arguments.

        Returns:
            None
        """
        df_dates = pd.DataFrame(
            {
                "date": pd.date_range(
                    start=f"{config.year}-01-01",
                    end=f"{config.year}-12-31",
                ),
            }
        )
        df_dates["count"] = random.sample(range(DEMO_MAX_COUNT), len(df_dates))

        csv_filename = Path(config.output_dir) / "sample.csv"
        csv_filename.parent.mkdir(parents=True, exist_ok=True)
        df_dates.to_csv(csv_filename, sep=",", index=False, header=False)
        logger.debug("Generate sample CSV file: %s", csv_filename)


class EnvironmentAction(argparse.Action):
    """Show environment details action."""

    def __init__(self, *nargs, **kwargs):
        """Overwrite class method."""
        kwargs["nargs"] = 0
        super().__init__(*nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Overwrite class method."""
        sys_version = sys.version.replace("\n", "")
        env = (
            f"heatmap: {__version__}\n"
            f"python: {sys_version}\n"
            f"platform: {platform.platform()}\n"
        )
        parser._print_message(env, sys.stdout)
        parser.exit()
