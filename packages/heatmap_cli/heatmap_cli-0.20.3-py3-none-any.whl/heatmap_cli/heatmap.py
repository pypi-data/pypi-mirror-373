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

"""Main logic to generate heatmap."""

import argparse
import copy
import logging
import multiprocessing
import re
import shutil
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image

# Generate matplotlib graphs without an X server.
# See http://stackoverflow.com/a/4935945
mpl.use("agg")

# Suppress logging from matplotlib in debug mode.
logging.getLogger("matplotlib").propagate = False
logger = multiprocessing.get_logger()


def run(config: argparse.Namespace) -> None:
    """Run the main flow.

    Args:
        config (argparse.Namespace): Config from command line arguments.

    Returns:
        None
    """
    logger.debug(config)
    logger.debug("number of cpu: %d", multiprocessing.cpu_count())

    _refresh_output_dir(config)

    if config.animate_by_week:
        _generate_animated_heatmap_by_week(config)
    else:
        _generate_heatmaps(config)


def _generate_animated_heatmap_by_week(config: argparse.Namespace) -> None:
    """Generate animated heatmap by week.

    Args:
        config (argparse.Namespace): Config from command line arguments.
    """
    start_of_week = datetime.strptime(
        f"{config.year}-W{config.week}-1", "%G-W%V-%u"
    ).date()
    dates_list = [start_of_week + timedelta(days=i) for i in range(7)]
    days_in_current_week = [d.strftime("%Y-%m-%d") for d in dates_list]

    for seq, day in enumerate(days_in_current_week, 1):
        config_for_heatmap = copy.copy(config)
        config_for_heatmap.end_date = day
        config_for_heatmap.open = False
        dataframe = _massage_data(config_for_heatmap)
        _generate_heatmap(seq, config.cmap[0], config_for_heatmap, dataframe)

    png_files = sorted(Path(config.output_dir).glob("*.png"))
    if not png_files:
        logger.warning("no PNG files found to create GIF animation.")
        return

    frames = [Image.open(png_files[0])]
    for png_path in png_files[1:]:
        frames.append(Image.open(png_path))

    config.format = "gif"
    title = _generate_title(config)
    img_filename = (
        Path.cwd()
        / config.output_dir
        / _generate_filename(config, 0, config.cmap[0], title)
    )
    img_filename.parent.mkdir(parents=True, exist_ok=True)

    frames[0].save(
        img_filename,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=1000,
        loop=0,
    )
    logger.info("generate animated heatmap: %s", img_filename)

    # remove temporary png files
    for png_path in png_files:
        try:
            png_path.unlink()
            logger.debug("removed temporary PNG file: %s", png_path)
        except OSError as e:
            logger.warning(
                "error removing temporary PNG file %s: %s", png_path, e
            )

    if config.open:
        _open_heatmap(img_filename)


def _generate_heatmaps(config: argparse.Namespace) -> None:
    """Generate regular heatmaps.

    Args:
        config (argparse.Namespace): Config from command line arguments.
    """
    dataframe = _massage_data(config)
    args = [
        (*seq_cmap, config, dataframe)
        for seq_cmap in enumerate(config.cmap, 1)
    ]
    logger.debug(args)

    # Fork, instead of spawn process (child) inherit parent logger config.
    # See https://stackoverflow.com/q/14643568
    with multiprocessing.get_context("fork").Pool() as pool:
        pool.starmap(_generate_heatmap, args)


def _massage_data(config: argparse.Namespace) -> pd.DataFrame:
    """Filter data from CSV file and structure it for the heatmap.

    Reads the input CSV, filters data based on the specified year and optional
    week/end date, ensures the full year's date structure is present, fills
    missing day counts with 0, and pivots the data for heatmap generation.

    Args:
        config (argparse.Namespace): Config from command line arguments.

    Returns:
        pd.DataFrame: Pivoted DataFrame ready for heatmap plotting.

    Raises:
        ValueError: If duplicate dates are found in the input file or if no
                    data is extracted for the specified period.
        FileNotFoundError: If the input CSV file does not exist.
    """
    # 1. Read CSV and initial processing
    try:
        dataframe = pd.read_csv(
            config.input_filename, header=None, names=["date", "count"]
        )
    except FileNotFoundError as e:
        logger.error("Input file not found: %s", config.input_filename)
        raise e

    dataframe["date"] = pd.to_datetime(dataframe["date"])

    # 2. Check for duplicates early
    duplicate_dates = dataframe[dataframe["date"].duplicated(keep=False)]
    if not duplicate_dates.empty:
        # Format duplicate dates for better readability in the error message
        dup_dates_str = ", ".join(
            duplicate_dates["date"].dt.date.astype(str).unique()
        )
        raise ValueError(f"Duplicate dates found: {dup_dates_str}")

    # Add calendar columns and apply count transformation
    # Monday=1..Sunday=7
    dataframe["weekday"] = dataframe["date"].dt.weekday + 1
    dataframe["year"] = dataframe["date"].dt.isocalendar().year
    dataframe["week"] = (
        dataframe["date"].dt.isocalendar().week.astype(str).str.zfill(2)
    )
    if config.annotate:
        dataframe["count"] = dataframe["count"].apply(_truncate_rounded_count)

    # 3. Filter data based on year and potentially week/end_date
    # Use >= 52 for week comparison to include potential week 53 in leap years
    # when user specifies --week 52 (meaning the whole year).
    if config.end_date:
        steps = dataframe.loc[
            (dataframe["year"] == config.year)
            & (dataframe["date"] <= config.end_date)
        ].copy()  # Use .copy() to avoid SettingWithCopyWarning
    elif config.week >= 52:
        # Filter only by year if week is 52 or 53
        steps = dataframe.loc[dataframe["year"] == config.year].copy()
    else:
        # Filter by year and week number (inclusive)
        steps = dataframe[
            (dataframe["year"] == config.year)
            & (dataframe["week"] <= str(config.week).zfill(2))
        ].copy()

    # 4. Check if filtered data is empty
    if steps.empty:
        raise ValueError(
            "No data extracted from CSV file for the specified period!"
        )

    logger.debug(
        "Last date in filtered data: %s",
        max(steps["date"]).date(),
    )

    # 5. Create the full structure for the target year
    start_date = pd.to_datetime(f"{config.year}-01-01")
    end_date = pd.to_datetime(f"{config.year}-12-31")
    full_year_dates = pd.date_range(start=start_date, end=end_date, freq="D")
    full_year_structure = pd.DataFrame({"date": full_year_dates})
    full_year_structure["weekday"] = full_year_structure["date"].dt.weekday + 1
    full_year_structure["week"] = (
        full_year_structure["date"]
        .dt.isocalendar()
        .week.astype(str)
        .str.zfill(2)
    )

    # 6. Merge filtered data into the full year structure
    # Select only necessary columns from steps for the merge
    steps_to_merge = steps[["date", "count"]]
    # Use left merge to keep all dates from full_year_structure
    merged_data = pd.merge(
        full_year_structure, steps_to_merge, on="date", how="left"
    )

    # 7. Fill missing counts with 0
    merged_data["count"] = merged_data["count"].fillna(0)
    # Ensure count is integer type after fillna (which might make it float)
    merged_data["count"] = merged_data["count"].astype(int)

    # 8. Pivot the table for the heatmap
    # The pivot operation will naturally handle the structure based on
    # weekday/week
    year_dataframe = merged_data.pivot_table(
        values="count", index=["weekday"], columns=["week"], fill_value=0
    )

    # Ensure all 53 potential week columns exist, filling missing ones with 0
    all_weeks = [str(w).zfill(2) for w in range(1, 54)]
    year_dataframe = year_dataframe.reindex(columns=all_weeks, fill_value=0)

    # Ensure all 7 weekday rows exist
    year_dataframe = year_dataframe.reindex(index=range(1, 8), fill_value=0)

    return year_dataframe


def _truncate_rounded_count(count: float) -> int:
    """Truncate and round count values to fit them in heatmap box.

    Rounds the count to the nearest hundred and then divides by 100.
    This transformation is applied when annotations are enabled to simplify
    large numbers and make them fit visually within the heatmap cells.
    For example, 12345 becomes 123, 5678 becomes 57.

    Args:
        count (int/float): The original count value.

    Returns:
        int: Truncated count value (divided by 100).
    """
    return int(round(count, -2) / 100)


def _generate_heatmap(
    seq: int,
    cmap: str,
    config: argparse.Namespace,
    dataframe: pd.DataFrame,
) -> None:
    """Generate a heatmap.

    Args:
        seq (int): Sequence number for generated heatmap image file.
        cmap (str): Colormap name used for the heatmap.
        config (argparse.Namespace): Config from command line arguments.
        dataframe (pd.core.frame.DataFrame): DataFrame with data loaded from
        CSV file.

    Returns:
        None
    """
    _, axis = plt.subplots(figsize=(8, 5))
    axis.tick_params(axis="both", which="major", labelsize=9)
    axis.tick_params(axis="both", which="minor", labelsize=9)

    cbar_options = {
        "orientation": "horizontal",
        "label": (
            f"Generated by: pypi.org/project/heatmap_cli, colormap: {cmap}"
        ),
        "pad": 0.10,
        "aspect": 60,
        "extend": "max",
    }
    options = {
        "ax": axis,
        "fmt": "",
        "square": True,
        "cmap": cmap,
        "cbar": config.cbar,
        "cbar_kws": cbar_options,
    }

    if config.cmap_min:
        options.update({"vmin": config.cmap_min})

    if config.cmap_max:
        options.update({"vmax": config.cmap_max})

    if config.annotate:
        cbar_options.update(
            {
                "label": f"{cbar_options['label']}, count: nearest hundred",
            }
        )
        options.update(
            {
                "annot": True,
                "annot_kws": {"fontsize": 8},
                "linewidth": 0,
            }
        )

    # Convert value larger than 100 to >1.
    res = sns.heatmap(dataframe, **options)
    for text in res.texts:
        count = int(float(text.get_text()))
        if count >= 100:
            text.set_text(">" + str(count)[0])
        else:
            text.set_text(count)

    if config.cbar:
        cbar = res.collections[0].colorbar
        cbar.set_label(
            cbar.ax.get_xlabel(), rotation=0, labelpad=8, loc="left"
        )

    title = _generate_title(config)
    img_filename = (
        Path.cwd()
        / config.output_dir
        / _generate_filename(config, seq, cmap, title)
    )
    img_filename.parent.mkdir(parents=True, exist_ok=True)

    axis.set_title(title, fontsize=11, loc="left")
    axis.set_title(config.author, fontsize=11, loc="right")
    plt.tight_layout()
    plt.savefig(
        img_filename,
        bbox_inches="tight",
        transparent=False,
        dpi=76,
        format=config.format,
    )
    logger.info("generate heatmap: %s", img_filename)

    if config.open:
        _open_heatmap(img_filename)


def _open_heatmap(filename: Path) -> None:
    """Open generated heatmap using the default program.

    Args:
        filename (str): The filename of the heatmap to open.

    Returns:
        None
    """
    file_uri = f"file://{filename.resolve()}"
    webbrowser.open(file_uri)
    logger.info("Open heatmap: %s using default program.", filename.resolve())


def _generate_filename(
    config: argparse.Namespace, seq: int, cmap: str, title_str: str
) -> str:
    """Generate an image filename based on the title.

    Args:
        config (argparse.Namespace): Config from command line arguments.
        seq (int): Sequence number for generated heatmap image file.
        cmap (str): Colormap name used for the heatmap.
        title_str (str): The title of the heatmap.

    Returns:
        str: A generated file name for the image.
    """
    annotated_suffix = "_annotated" if config.annotate else ""
    animated_suffix = "_animated" if config.format == "gif" else ""

    # Sanitize title_str for filename
    s = title_str.strip().lower()
    s = re.sub(r"\s+", "_", s)  # Replace spaces with single underscore
    # Remove characters not alphanumeric, underscore, dot, or hyphen
    s = re.sub(r"[^\w._-]+", "", s)
    # Limit length to prevent overly long filenames
    sanitized_title_part = s[:100]

    return (
        f"{seq:03d}_{sanitized_title_part}_{cmap}{annotated_suffix}{animated_suffix}"
        f".{config.format}"
    )


def _generate_title(config: argparse.Namespace) -> str:
    """Generate a title for the heatmap.

    Args:
        config (argparse.Namespace): Config from command line arguments.

    Returns:
        str: A generated title for the heatmap.
    """
    if not config.title:
        title = f"Year {config.year}: Total Daily Walking Steps"
        # If config.week is less than 52, it means a partial year is requested.
        # config.week >= 52 implies the whole year data is used (as per
        # _massage_data logic).
        if config.week < 52:
            title += f" Through Week {config.week:02d}"
    else:
        title = config.title

    logger.debug(title)
    return title


def _refresh_output_dir(config: argparse.Namespace) -> None:
    """Delete and recreate the output folder.

    Args:
        config (argparse.Namespace): Config from command line arguments.

    Returns:
        None
    """
    output_dir = _get_output_dir(config)

    # Determine if purging is required based on --purge and --yes flags.
    should_purge = False
    if config.purge:
        if config.yes:
            should_purge = True
        else:
            prompt = (
                f"Are you sure to purge output folder: {output_dir}? [y/N] "
            )
            if input(prompt).lower() in ["y", "yes"]:
                should_purge = True

    # If purging is required and the directory exists, remove it.
    if should_purge and output_dir.exists():
        logger.info("Purging output folder: %s", output_dir.absolute())
        try:
            shutil.rmtree(output_dir)
        except OSError as e:
            logger.error("Error removing directory: %s - %s.", output_dir, e)
            # Depending on desired error handling, you might want to raise an exception here.
            return

    # Ensure the output directory exists for writing files.
    # This will create it if it doesn't exist or was just purged.
    logger.info("Ensuring output folder exists: %s", output_dir.absolute())
    output_dir.mkdir(parents=True, exist_ok=True)


def _get_output_dir(config: argparse.Namespace) -> Path:
    """Get the current working directory.

    Args:
        config (argparse.Namespace): Config from command line arguments.

    Returns:
        str: The output directory path.
    """
    output_dir = Path(config.output_dir)
    if output_dir.is_absolute():
        return output_dir

    return Path.cwd() / config.output_dir
