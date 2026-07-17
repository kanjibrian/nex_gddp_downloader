"""
Progress bar helpers using tqdm.
"""

from __future__ import annotations

from tqdm import tqdm


def create_file_progress(
    filename: str,
    total_size: int | None,
    initial: int = 0,
) -> tqdm:
    """
    Create a tqdm progress bar for a single file download.

    Parameters
    ----------
    filename : str
        Display name shown in the progress bar.
    total_size : int | None
        Total file size in bytes (``None`` for unknown).
    initial : int
        Starting byte count (for resumed downloads).
    """

    return tqdm(
        total=total_size,
        initial=initial,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=filename,
        leave=False,
        miniters=1,
    )


def create_overall_progress(total_files: int) -> tqdm:
    """
    Create a tqdm progress bar tracking the number of files processed.
    """

    return tqdm(
        total=total_files,
        unit="file",
        desc="Overall",
        position=0,
        leave=True,
    )
