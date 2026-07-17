"""
Entry point for the NASA NEX-GDDP-CMIP6 downloader.
"""

from __future__ import annotations

import sys
import time

from config import load_config
from downloader.download import Downloader
from downloader.filters import filter_catalog
from downloader.index import read_catalog
from downloader.logger import setup_logger
from downloader.utils import format_duration
from downloader.validators import print_summary, validate_selection


def create_directories(config) -> None:
    """Ensure output directories exist."""

    config.download_directory.mkdir(parents=True, exist_ok=True)
    config.log_directory.mkdir(parents=True, exist_ok=True)


def main() -> None:

    print("=" * 60)
    print("  NASA NEX-GDDP-CMIP6 Downloader")
    print("=" * 60)

    try:

        # ---------------------------------------------------------
        # Load configuration
        # ---------------------------------------------------------

        config = load_config()

        create_directories(config)

        # ---------------------------------------------------------
        # Set up logging
        # ---------------------------------------------------------

        log = setup_logger(config.log_directory)

        log.info("Configuration loaded from settings.yml")
        log.debug(
            "Workers: %d | Timeout: %ds | Chunk: %d MB",
            config.workers,
            config.timeout,
            config.chunk_size_mb,
        )

        # ---------------------------------------------------------
        # Read NASA catalogue
        # ---------------------------------------------------------

        catalog = read_catalog(config)
        log.info("Catalogue contains %s files.", f"{len(catalog):,}")

        # ---------------------------------------------------------
        # Apply filters
        # ---------------------------------------------------------

        files = filter_catalog(catalog, config)

        validate_selection(files)
        print_summary(files)

        # ---------------------------------------------------------
        # Download
        # ---------------------------------------------------------

        start_time = time.time()

        downloader = Downloader(config)
        downloader.download_all(files)

        elapsed = time.time() - start_time
        log.info("Total time: %s", format_duration(elapsed))

        print("\nDone.")

    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)

    except Exception as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()