"""
Utility helpers for the NEX-GDDP-CMIP6 downloader.
"""

from __future__ import annotations


def format_size(size_bytes: int | float) -> str:
    """
    Convert a byte count into a human-readable string.

    Examples
    --------
    >>> format_size(1024)
    '1.00 KB'
    >>> format_size(1_500_000)
    '1.43 MB'
    """

    if size_bytes < 0:
        return "0 B"

    units = ("B", "KB", "MB", "GB", "TB")
    value = float(size_bytes)

    for unit in units[:-1]:
        if abs(value) < 1024.0:
            return f"{value:.2f} {unit}"
        value /= 1024.0

    return f"{value:.2f} {units[-1]}"


def format_duration(seconds: float) -> str:
    """
    Convert seconds into a human-readable duration string.

    Examples
    --------
    >>> format_duration(3661)
    '1h 01m 01s'
    >>> format_duration(45)
    '45s'
    """

    seconds = max(0, int(seconds))

    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    if minutes:
        return f"{minutes}m {secs:02d}s"

    return f"{secs}s"
