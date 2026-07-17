"""
Functions for downloading and reading the official NASA THREDDS file index.
"""

from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
import requests
from config import Config
from downloader.models import ClimateFile
from downloader.catalog import Catalog

CSV_NAME = "gddp_catalog.csv"

# ---------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------

def download_catalog(config: Config) -> Path:
    """
    Download the official NASA CSV catalogue.

    The file is cached inside the log directory so it
    is only downloaded once.
    """

    cache = config.log_directory / CSV_NAME

    if cache.exists():
        print("Using cached catalogue.")
        return cache

    print("Downloading NASA catalogue...")

    response = requests.get(
        config.catalog_csv,
        timeout=config.timeout
    )

    response.raise_for_status()

    cache.write_bytes(response.content)

    print("Catalogue downloaded.")

    return cache


# ---------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------

def read_catalog(config: Config) -> list[ClimateFile]:

    csv_file = download_catalog(config)

    df = pd.read_csv(
        csv_file,
        usecols=["fileMD5", "fileUrl"],
        skipinitialspace=True,
    )

    files = [parse_row(row.fileUrl, row.fileMD5) for row in df.itertuples(index=False)]

    return Catalog(files)


# ---------------------------------------------------------------------
# Parse URL
# ---------------------------------------------------------------------

YEAR_PATTERN = re.compile(r"(\d{4})\.nc$")


def parse_row(
    url: str,
    md5: str
) -> ClimateFile:
    """
    Convert a download URL into a ClimateFile object.

    Example URL

    https://.../ACCESS-CM2/ssp245/r1i1p1f1/pr/
    pr_day_ACCESS-CM2_ssp245_r1i1p1f1_gn_2050.nc
    """

    parts = url.split("/")

    model = parts[-5]
    scenario = parts[-4]
    ensemble = parts[-3]
    variable = parts[-2]

    filename = parts[-1]

    match = YEAR_PATTERN.search(filename)

    if match is None:
        raise ValueError(
            f"Cannot determine year from\n{filename}"
        )

    year = int(match.group(1))

    relative = Path(
        model,
        scenario,
        ensemble,
        variable,
        filename
    )

    return ClimateFile(

        model=model,
        scenario=scenario,
        ensemble=ensemble,
        variable=variable,
        year=year,
        url=url,
        md5=md5,
        relative_path=relative
    )